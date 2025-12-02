import pandas as pd
import numpy as np
import statsmodels.api as sm
import tsfresh as tsf

from ACF import (check_stationarity, 
                differienciate_time_series,
                compute_significant_positive_lags,
                plot_acf_and_significant_lags,
                compute_fundamental_interval_with_decay_threshold
                )


def create_feature_in_dataframe(data_array, df_fundamental_interval, threshold=0.5):
    """This function creates a dataframe with all the features for each file.
    Arguments:
        - data_array (Array) = the array with the data that have already been pre-processed
        - df_fundamentl_period (DataFrame): 
        - threshold (float): thresholdvalue to compute counts above threshold
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
                              np.median(energy_single_time_series),
                              np.median(mean_single_time_series),
                              np.median(count_above_threshold_single_time_series),
                              np.median(absolute_sum_of_changes_single_time_series),
                              np.median(quantile_time_series),
                              np.median(standard_deviation_single_time_series),
                              np.median(count_above_mean_single_time_series)
                              ]],
                            columns=['Video name',
                                     'Contraction power',
                                     'Mean',
                                     '%_of_count_above_threshold',
                                     '%_of_absolute_sum_of_changes',
                                     'Quantile_75',
                                     'Standard_deviation',
                                     '%_of_count_above_mean'
                                     ])

        df_data = pd.concat([df_data, df_0], axis=0, ignore_index=True)
    # Merge ACF dataframe with other features
    if df_fundamental_interval is not None:
        df_data = pd.merge(df_data, df_fundamental_interval, on='Video name', how='outer')

    return df_data


def extract_acf_values(
        data_array, 
        image_path,
        ):
    """This function computes the ACF values and extract the fundamental interval for each observation
    Arguments:
    - data (array): the array with the data that have already been pre-processed (especially detrending is important)
    Returns:
    - fundamenta_interval (series): column containing the fundamental interval for each observation
    """
    fundamental_interval_single_time_series = []
    for file in range(len(data_array)):
        data = data_array[file][1] 
        # Step 1: Preprocessing and avarage over the 10 time series (representing the 10 different points of the organoids)
        avaraged_data = [sum(x) / len(data) for x in zip(*data)]

        # Step 2: Check stationarity and differienciate
        stationarity_flag = check_stationarity(avaraged_data)
        avaraged_data = differienciate_time_series(stationarity_flag, avaraged_data)

        # Step 3: Calculate ACF values and confidence intervals using Bartlett's formula
        # If you want constant confidence bands, set bartlett_confint=False
        acf_values, confint = sm.tsa.acf(avaraged_data,
                                        alpha=0.05, #confidence interval 95%
                                        nlags=6000,
                                        bartlett_confint=True,
                                        )
        
        # Step 4 and 5: Recenter CI, necessary to have the confidence intervals centered to zero (the confint are centered around the ACF value)
        # Find the significant lags where ACF values are outside the confidence intervals 
        significant_lags, centered_ci = compute_significant_positive_lags(acf_values=acf_values,
                                                                        confint=confint,
                                                                        )
        plot_acf_and_significant_lags(
            input_data=avaraged_data,
            input_name= data_array[file][0],
            image_path=image_path,
            acf_values=acf_values,
            significant_lags=significant_lags,
            plotted_lags=6000,
            alpha=0.05,
            )   

        #Step 6 and 7:
        fundamental_interval = compute_fundamental_interval_with_decay_threshold(acf_values, centered_ci, significant_lags)
        fundamental_interval_single_time_series.append((data_array[file][0], fundamental_interval))
    # create DataFrame using 
    df_fundamental_interval_single_time_series = pd.DataFrame(fundamental_interval_single_time_series, columns = ['Video name', 'Fundamental interval [s]'])
    return df_fundamental_interval_single_time_series
 