from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import ipywidgets as ipyw

import numpy as np
from .time_series_extraction import get_binary_opening, get_wo_small_objects, get_canny_edges

class Viewer():
  def __init__(self, img):
    self.img = img
    otsu_thresholds = get_mutli_otsu_thresholds(self.img)
    self.mask = apply_thresholds(self.img, otsu_thresholds)
    #self.mask = remove_holes_and_objects(self.mask)
    self.n_ratio, self.m_ratio = compute_nm_ratio(self.mask)
    self.thresh0, self.thresh1 = otsu_thresholds
    self.total_pixel_counts = compute_total_pixel_counts(self.mask)
    fig_title = 'Muscle part: '+str(self.m_ratio)+', Neural part: '+str(self.n_ratio)

    # Setup figure properties and add the image to the plot
    self.fig, self.ax = plt.subplots()
    original_img = self.ax.imshow(self.img, cmap='gray')
    self.ax.set_axis_off()
    self.ax.set_title(fig_title)
    axis_color = 'lightgoldenrodyellow'

    # Define an axes area and draw a slider in it
    thresh0_slider_ax  = self.fig.add_axes([0.25, 0.05, 0.5, 0.02], facecolor=axis_color)
    self.thresh0_slider = Slider(thresh0_slider_ax, 'Muscle Threhsold', 0.0, 1.0, valinit=self.thresh0)
    self.thresh0_slider.on_changed(self.sliders_on_changed)

    # Draw another slider
    threh1_slider_ax = self.fig.add_axes([0.25, 0.0, 0.5, 0.02], facecolor=axis_color)
    self.thresh1_slider = Slider(threh1_slider_ax, 'Neural Threhsold', 0.0, 1.0, valinit=self.thresh1)
    self.thresh1_slider.on_changed(self.sliders_on_changed)

    # Add a button for resetting the parameters
    reset_button_ax = self.fig.add_axes([0.9, 0.025, 0.1, 0.04])
    reset_button = Button(reset_button_ax, 'Reset', color=axis_color, hovercolor='0.975')
    reset_button.on_clicked(self.reset_button_on_clicked)

    # Add a checkbox to switch between views
    radio_ax = self.fig.add_axes([0.8, 0.8, 0.18, 0.2])
    radio_btn = RadioButtons(radio_ax, ('mask on', 'mask off'))
    radio_btn.on_clicked(self.change_view)

    # Overlay the mask on the image
    self.masked_array = np.ma.masked_array(self.mask, ~self.mask.astype(bool))
    self.masked_image = self.ax.imshow(self.masked_array, cmap='viridis')
    plt.show()

  # Define an action for modifying the image when any slider's value changes
  def sliders_on_changed(self, val):
    self.mask = apply_thresholds(self.img, (self.thresh0_slider.val, self.thresh1_slider.val))
    #self.mask = remove_holes_and_objects(self.mask)
    self.n_ratio, self.m_ratio = compute_nm_ratio(self.mask)
    self.total_pixel_counts = compute_total_pixel_counts(self.mask)
    self.masked_image.set_array(np.ma.masked_array(self.mask, ~self.mask.astype(bool)))
    self.fig.canvas.draw_idle()
    self.ax.set_title('Muscle part: '+str(self.m_ratio)+', Neural part: '+str(self.n_ratio)+',\n Total_pixel_counts:'+str(self.total_pixel_counts))

  # Update the threshold values once the reset button has been clicked
  def reset_button_on_clicked(self, mouse_event):
    self.thresh0_slider.reset()
    self.thresh1_slider.reset()

  # Switch between simple image view and overlay with mask view
  def change_view(self, label):
    if label=='mask on':
      self.masked_image.set_array(np.ma.masked_array(self.mask, ~self.mask.astype(bool)))
    else:
      self.masked_image.set_array(np.ma.masked_array(self.img, ~np.zeros(self.img.shape).astype(bool)))
    self.fig.canvas.draw_idle()

  def get_ratios(self):
    return self.n_ratio, self.m_ratio

  def get_mask(self):
    return self.mask

  def get_thresholds(self):
    return self.thresh0_slider.val, self.thresh1_slider.val

  def get_total_pixel_counts(self):
    return self.total_pixel_counts

# Switch between simple image view and overlay with mask view
def change_view(label):
  if label=='mask on':
    masked_image.set_array(np.ma.masked_array(mask_pp, ~mask_pp.astype(bool)))
  else:
    masked_image.set_array(np.ma.masked_array(img, ~np.zeros(img.shape).astype(bool)))
  fig.canvas.draw_idle()



class ImageSliceViewer3D:
    """
    ImageSliceViewer3D is for viewing volumetric image slices in jupyter or
    ipython notebooks.

    User can interactively change the slice plane selection for the image and
    the slice plane being viewed.

    Argumentss:
    Volume = 3D input image
    figsize = default(8,8), to set the size of the figure
    cmap = default('plasma'), string for the matplotlib colormap. You can find
    more matplotlib colormaps on the following link:
    https://matplotlib.org/users/colormaps.html

    """

    def __init__(self, volume_g, volume, threshold, figsize=(15,15), cmap='gray'):
        self.volume_g = volume_g
        self.volume = volume
        self.threshold = threshold
        self.figsize = figsize
        self.cmap = cmap
        self.v = [np.min(volume), np.max(volume)]

        # Call to view a slice within the selected slice plane
        ipyw.interact(self.change_thresh,
            t=ipyw.FloatSlider(value=self.threshold, min=0, max=1, step=0.01, continuous_update=False,
            description='Threshold:', readout_format='.2f'))

    def change_thresh(self, t):
      mask = self.volume_g > t
      self.img_copy = self.volume.copy()
      bar = ipyw.IntProgress(value=0, min=0, max=len(range(mask.shape[0])), description='Loading:',
                       bar_style='', # 'success', 'info', 'warning', 'danger' or ''
                       #style={'bar_color': 'maroon'},
                       #orientation='horizontal'
                       )
      display(bar)
      for i in range(mask.shape[0]):
        bar.value = i
        mask[i] = get_binary_opening(mask[i])
        mask[i] = get_wo_small_objects(mask[i])
        mask[i] = get_canny_edges(mask[i], 3)
        img_temp = self.volume[i].copy()
        img_temp[mask[i]==1] = 255
        self.img_copy[i] = img_temp

      bar.bar_style = 'success'
      maxZ = self.volume.shape[0] - 1
      ipyw.interact(self.plot_slice,
          z=ipyw.IntSlider(min=0, max=maxZ, step=1, continuous_update=False,
          description='Time Frames:', layout=ipyw.Layout(width='100%')))


    def plot_slice(self, z):
        # Plot slice for the given plane and slice
        self.fig = plt.figure(figsize=self.figsize)
        plt.imshow(self.img_copy[z], cmap=plt.get_cmap(self.cmap),
            vmin=self.v[0], vmax=self.v[1])