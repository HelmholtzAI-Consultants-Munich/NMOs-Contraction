import pandas as pd
import numpy as np
import tsfresh as tsf


def create_feature_in_dataframe(data_array, contraction_class, threshold=0.5):
    """This function creates a dataframe with all the features for each file.
     data_array = the array with the data that have already been pre-processed - in main  data_no_processed,
     data_weak_processed, and data_strong_processed
     file_name_no = list of filenames per category
     contraction_class = 0, 1, 2 respectively for no, weak and strong contraction
     threshold = float to fix threshold to compute counts above threshold
     """
    scaling_time = 0.097
    df_data = pd.DataFrame()
    for file in range(len(data_array)):
        mean_single_time_series = []
        energy_single_time_series = []
        count_above_mean_single_time_series = []
        count_above_threshold_single_time_series = []
        absolute_sum_of_changes_single_time_series = []
        quantile_time_series = []
        standard_deviation_single_time_series = []
        for i in range(len(data_array[file])):
            # Energy
            energy = tsf.feature_extraction.feature_calculators.abs_energy(data_array[file][1][i]) \
                     / (len(data_array[file][1][i]) * scaling_time)
            energy_single_time_series.append(energy)
            # Mean
            mean_ts = np.mean(data_array[file][1][i])
            mean_single_time_series.append(mean_ts)
            # Count above the mean
            count_above_mean = tsf.feature_extraction.feature_calculators.count_above_mean(data_array[file][1][i]) / \
                               len(data_array[file][1][i])
            count_above_mean_single_time_series.append(count_above_mean)
            # Count above
            count_above_threshold = tsf.feature_extraction.feature_calculators.count_above(data_array[file][1][i],
                                                                                           threshold)
            count_above_threshold_single_time_series.append(count_above_threshold)
            # Absolute sum of changes
            absolute_sum_of_changes = tsf.feature_extraction.feature_calculators.absolute_sum_of_changes(
                data_array[file][1][i]) / (len(data_array[file][1][i]) - 1)
            absolute_sum_of_changes_single_time_series.append(absolute_sum_of_changes)
            # Quantile
            quantile = tsf.feature_extraction.feature_calculators.quantile(data_array[file][1][i], 0.75)
            quantile_time_series.append(quantile)
            # Standard deviation
            standard_deviation = tsf.feature_extraction.feature_calculators.standard_deviation(data_array[file][1][i])
            standard_deviation_single_time_series.append(standard_deviation)
            # Large standard deviation

        df_0 = pd.DataFrame([[data_array[file][0],
                              contraction_class,
                              np.median(energy_single_time_series),
                              np.median(mean_single_time_series),
                              np.median(count_above_threshold_single_time_series),
                              np.median(absolute_sum_of_changes_single_time_series),
                              np.median(quantile_time_series),
                              np.median(standard_deviation_single_time_series),
                              np.median(count_above_mean_single_time_series)
                              ]],
                            columns=['Video name',
                                     'Class',
                                     'Energy',
                                     'Mean',
                                     '%_of_count_above_threshold',
                                     '%_of_absolute_sum_of_changes',
                                     'Quantile_75',
                                     'Standard_deviation',
                                     '%_of_count_above_mean'
                                     ])

        df_data = pd.concat([df_data, df_0], axis=0, ignore_index=True)

    return df_data
