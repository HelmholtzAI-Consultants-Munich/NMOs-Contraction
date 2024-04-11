import numpy as np
from math import degrees, atan

from scipy.ndimage import binary_fill_holes
from skimage.feature import canny
from skimage.filters import threshold_otsu, gaussian, threshold_multiotsu
from skimage.transform import rotate
from skimage.morphology import disk, binary_opening, remove_small_objects, opening
from skimage.measure import label, regionprops

def get_canny_edges(img, sigma):
    return canny(img, sigma)

def get_binary_opening(img, disk_size=4):
    return binary_opening(img, disk(disk_size))

def get_wo_small_objects(img, min_size=400):
    return remove_small_objects(img, min_size=min_size)

def compute_gaussian(img, sigma):
    return gaussian(img, sigma)
    
def remove_border_points(border_points):
    '''Remove the white pixels on border of image'''
    border_x = list(border_points[0])
    border_y = list(border_points[1])
    i = 0
    remove_ids = []
    for x, y in zip(border_x, border_y):
        if x<2 or x>252 or y<5 or y>252: remove_ids.append(i)
        i+=1
    for i in reversed(remove_ids):
        border_x.pop(i)
        border_y.pop(i)
    return (np.array(border_x), np.array(border_y))

def get_thresh(img_slice0, sigma_smooth=2):
  img_smooth = compute_gaussian(img_slice0, sigma_smooth)
  thresh = threshold_otsu(img_smooth)
  return thresh, np.min(img_smooth), np.max(img_smooth)

def extract_border(img_slice, thresh, sigma_smooth=2, sigma_edge=3):
    '''
    Extract the border from a single frame, by following:
    1. Threshold image using Otsu thresholding
    2. Apply morphological opening and fill any holes in the binary image
    3. Compute edges using the Canny edge Detection algorithm
    4. Remove white pixels from border of image
    6. Return border coordinates and binary image
    '''
    img_smooth = compute_gaussian(img_slice, sigma_smooth)
    image_thresh = img_smooth > thresh
    image_thresh = get_binary_opening(image_thresh)
    image_thresh = remove_small_objects(image_thresh)

    edges = get_canny_edges(image_thresh, sigma_edge)
    x,y = remove_border_points((np.where(edges)))

    return (x,y), image_thresh

def sort_border(x,y):
    ''' Sort border pixels such that the signal coordinates are continuous'''
    sorted_x = x[np.argsort(x)] # sort x values
    sorted_y = y[np.argsort(y)] # sort y values
    max_dist_x = sorted_x[-1] - sorted_x[0] # compute max distance on x axis
    max_dist_y = sorted_y[-1] - sorted_y[0] # compute max distance on y axis
    # if x changes more than y
    if max_dist_x > max_dist_y: point0 = np.where(x==sorted_x[0])[0][0] # sort (x,y) points according to x
    # else sort (x,y) points according to y
    else: point0 = np.where(y==sorted_y[0])[0][0]

    sorted_ids = np.argsort((x-x[point0])**2+(y-y[point0])**2) # x+y
    x = x[sorted_ids]
    y = y[sorted_ids]
    return (x,y)

def get_border_angle(x , y):
    ''' Compute the angle of the border considering it as a line from first to last point'''
    xl = x[-1] - x[0]
    yl = y[-1] - y[0]
    theta = degrees(atan(xl/yl))
    # if theta is negative and the border is sorted according to x we want to rotate counter-clockwise
    # and by 180+theta to make sure x[0], y[0] moves to the begining of the signal
    if y[0] > y[-1]: theta = 180+theta
    return theta

# Get the two threhsolds for the image using multi-otsu thresholding
def get_mutli_otsu_thresholds(img):
  thresholds = threshold_multiotsu(img, classes=3)
  return thresholds

# Apply the threhsolds from the otsu method and generate a mask
def apply_thresholds(img, thresholds):
  mask = np.zeros(img.shape, dtype=np.uint8)
  mask[img<thresholds[1]] = 9 # neural threshold
  mask[img<thresholds[0]] = 4 # muscle threshold
  return mask

# Remove small areas and holes from both neural and muscle parts
def remove_holes_and_objects(mask, min_size=500): #1000
  label_mask = label(mask)
  # removed objects smaller than min_size
  for region in regionprops(label_mask):
      if region.area<min_size:
          mask[label_mask==region.label] = 0
          
  mask_n = np.zeros_like(mask)
  mask_n[mask==4] = 1
  mask_m = np.zeros_like(mask)
  mask_m[mask==9] = 1
  # fill holes
  mask_n = binary_fill_holes(mask_n)
  mask_n = opening(mask_n, disk(4))
  mask_m = binary_fill_holes(mask_m)
  mask_m = opening(mask_m, disk(4))

  mask[mask_m!=0] = 9
  mask[mask_n!=0] = 4
  return mask
    
# Compute the ratio of neural and muscle parts on the organoid mask
def compute_nm_ratio(mask):
  n_pix = np.sum(mask==9)
  m_pix = np.sum(mask==4)
  if n_pix==0 and m_pix==0: return 0, 0
  return np.round(n_pix/(n_pix+m_pix), 2), np.round(m_pix/(n_pix+m_pix),2)

#Compute the total number of pixel of the organoid
def compute_total_pixel_counts(mask):
  n_pix = np.sum(mask==9)
  m_pix = np.sum(mask==4)
  return n_pix + m_pix


def extract_signal(img_array, thresh):

  border_size = []
  med_y = []
  rotated_masks = []
  num_frames = img_array.shape[0]
  print('Going to use threshold: ', thresh)

  # and go a second time over to extract signals
  for frame_id in range(num_frames):

    # extract border and sort pixels
    (x,y), _ = extract_border(img_array[frame_id], thresh)
    x, y = sort_border(x, y)
    # Rotate border so that is always parallel to x-axis
    theta = get_border_angle(x , y)
    mask = np.zeros(img_array[frame_id].shape, dtype=bool)
    mask[(x,y)] = True #size 256, 256
    mask_r = rotate(mask, theta, resize=True) # shape usually 305,305 but changes

    # store rotated image and length of border
    y = np.sort(np.where(mask_r)[1])
    dist_y = y[-1] - y[0]
    med_y.append(dist_y//2 + y[0])
    border_size.append(dist_y)
    rotated_masks.append(mask_r)

  # get minimum border length and where the border is minimized
  border_size = np.array(border_size)
  bbox_size = np.min(border_size)
  median_y = med_y[np.argmin(border_size)]

  if bbox_size%2==1: bbox_size-=1
  if bbox_size<100:
    print('The organoid is moving strongly in this video and the border is not enitrely visible in the scene in all frames.\n',
    'For this reason we will only export signals for 5 sub-regions of the border')
    subsample_regions = 5
  else:
    subsample_regions = 10
  distances = np.zeros((subsample_regions, num_frames))
  x_crop = 250

  del border_size
  del img_array
  del x
  del y
  del mask

  for frame_id in range(num_frames):

    mask_r = rotated_masks[frame_id]

    # Pad so we always have a fixed size image
    resize_size = (1024 - mask_r.shape[0], 512 - mask_r.shape[1])
    mask_r = np.pad(mask_r, ((resize_size[0]//2+mask_r.shape[0]%2, resize_size[0]//2), (resize_size[1]//2+mask_r.shape[1]%2, resize_size[1]//2)))

    # readjust median y to new img size
    median_yf = median_y + resize_size[1]//2+mask_r.shape[1]%2

    # Translate always relative to middle of image and around median of columns
    if frame_id==0:
      where_border = np.where(mask_r)
      mean_x = round(np.mean(where_border[0]))

    # crop edges of border so hopefully we are always including the same border points
    mask_r = mask_r[mean_x-x_crop:mean_x+x_crop, median_yf-bbox_size//2:median_yf+bbox_size//2]\

    # get new img size and size of subsampled regions
    new_height, new_width = mask_r.shape
    subsample_area = new_width//subsample_regions

    # get the average of coordinates in sub-region along the x-axis and subtract from average if frame0
    for i in range(subsample_regions):
      sub_area = mask_r[:,i*subsample_area:(i+1)*subsample_area]
      x_sub, _ = np.where(sub_area)
      distances[i, frame_id] = np.mean(x_sub)

  return distances, subsample_regions




