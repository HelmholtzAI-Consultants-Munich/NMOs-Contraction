import numpy as np
import pandas as pd

def process_single_ts(data_array, norm=False, de_trend=True, degree=6, smooth=True, smooth_n=20):

  # clip signal at +/- 20 pixels
  # np.clip(data_array, -20, 20, out=data_array)

  # Fill NaNs through polynomial interpolation
  is_nan = False
  for i in range(data_array.shape[0]):
    if sum(np.isnan(data_array[i, :])):
      series = pd.Series(data_array[i, :])
      series.interpolate(method='polynomial', order=5, inplace=True)
      data_array[i, :] = series.to_numpy()
      is_nan = True

  # convert pixel in micrometer
  conversion_factor = 1.0130737254901963
  data_array *= conversion_factor

  # normalize time series
  if norm:
      mean = np.mean(data_array, axis=1).reshape(-1, 1)
      std = np.std(data_array, axis=1).reshape(-1, 1)
      data_array = (data_array - mean) / std

  # de-trend data
  trend = np.zeros(data_array.shape)
  if de_trend:
      for i in range(data_array.shape[0]):
          x = np.linspace(0, data_array[0, :].shape[0], data_array[0, :].shape[0])
          y = data_array[i, :]
          model = np.polyfit(x, y, degree)
          trend[i, :] = np.polyval(model, x)

  # de-trend with another method using first difference

  data_array -= trend

  # smooth (moving average to reduce noise)
  if smooth:
      data_smooth = np.zeros((data_array.shape[0], data_array.shape[1] - (smooth_n - 1)))
      for i in range(data_array.shape[0]):
          data_smooth[i, :] = np.convolve(data_array[i, :], np.ones(smooth_n) / smooth_n, mode='valid')
      data_array = data_smooth

  return data_array, is_nan
