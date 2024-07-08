from matplotlib import pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons
import ipywidgets as ipyw

import numpy as np
from time_series_extraction import get_mutli_otsu_thresholds, apply_thresholds, compute_nm_ratio, compute_total_area, get_binary_opening, get_wo_small_objects, get_canny_edges

from joblib import Parallel, delayed, cpu_count


class Viewer():
  def __init__(self, img):
    self.img = img
    otsu_thresholds = get_mutli_otsu_thresholds(self.img)
    self.mask = apply_thresholds(self.img, otsu_thresholds)
    #self.mask = remove_holes_and_objects(self.mask)
    self.n_ratio, self.m_ratio = compute_nm_ratio(self.mask)
    self.thresh0, self.thresh1 = otsu_thresholds
    self.total_area = compute_total_area(self.mask)
    fig_title = 'Muscle part: '+str(self.m_ratio)+', Neural part: '+str(self.n_ratio)+',\n Total_area: '+str(round(self.total_area, 3))+' mm^2'

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
    self.total_area = compute_total_area(self.mask)
    self.masked_image.set_array(np.ma.masked_array(self.mask, ~self.mask.astype(bool)))
    self.fig.canvas.draw_idle()
    self.ax.set_title('Muscle part: '+str(self.m_ratio)+', Neural part: '+str(self.n_ratio)+',\n Total_area: '+str(self.total_area)+' mm^2')

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

  def get_total_area(self):
    return self.total_area


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

    def __init__(self, volume_g, volume, threshold, cmap='gray'):
        self.volume_g = volume_g
        self.volume = volume
        self.threshold = threshold
        self.cmap = cmap
        self.v = [np.min(volume), np.max(volume)]
        
        # Call to view a slice within the selected slice plane
        ipyw.interact(self.change_thresh,
            t=ipyw.FloatSlider(value=self.threshold, min=0, max=1, step=0.01, continuous_update=False,
            description='Threshold:', readout_format='.2f'))

    def change_thresh(self, t):
        mask = self.volume_g > t
        bar = ipyw.IntProgress(value=0, min=0, max=len(range(mask.shape[0])), description='Loading:',bar_style='')
        display(bar)

        images = Parallel(n_jobs=cpu_count() - 2, backend='threading')(
            delayed(self._process_image)(mask[i], self.volume[i], bar) for i in range(mask.shape[0])
        )
        self.img_copy = np.array(images)
        
        bar.bar_style = 'success'
        maxZ = self.volume.shape[0] - 1
        ipyw.interact(self.plot_slice,
          z=ipyw.IntSlider(min=0, max=maxZ, step=1, continuous_update=False,
          description='Time Frames:', layout=ipyw.Layout())) #width='100%')))

    
    def _process_image(self, mask, image_slice, bar):
        bar.value += 1
        mask = get_binary_opening(mask)
        mask = get_wo_small_objects(mask)
        mask = get_canny_edges(mask, 3)
        image = image_slice.copy()
        image[mask==1] = 255
        return image


    def plot_slice(self, z):
        # Plot slice for the given plane and slice
        self.fig = plt.figure()
        plt.axis('off')
        plt.imshow(self.img_copy[z], cmap=plt.get_cmap(self.cmap),
            vmin=self.v[0], vmax=self.v[1])
        plt.show()
