# This utils file contains all the functions needed for the extraction of the fundamental interval feature
import numpy as np
import os
import matplotlib.pyplot as plt

from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf



def check_stationarity(series):
    # From https://machinelearningmastery.com/time-series-data-stationary-python/
    """This function check stationarity by performing tha Augmented Dickey-Fuller unit root test
    Arguments:
    - series (array-like): array or list containing the time series
    Returns:
    - None
    It prints whether the time series is stationary or not (respectivelt rejects or accept the null hypotesis)"""

    result = adfuller(series)

    # print('ADF Statistic: %f' % result[0])
    # print('p-value: %f' % result[1])
    # print('Critical Values:')
    # for key, value in result[4].items():
    #     print('\t%s: %.3f' % (key, value))

    if (result[1] <= 0.05) & (result[4]['5%'] > result[0]):
        # print("\u001b[32mStationary\u001b[0m")
        stationarity_flag = True
    else:
        # print("\x1b[31mNon-stationary\x1b[0m")
        stationarity_flag = False
    return stationarity_flag


def differienciate_time_series(
        stationarity_flag,
        data
        ):
    """This function differentiate the time series only if the stationary lag equals False,
    meaning that the time series does not have a unit root and it not stationary.
    This is done because autocorrelation assumes the stationarity.
    Arguments:
    - stationarity_flg (bool): True if time series stationary, False if not stationary. It's the return of check_stationarity function
    - data (array-like): array containing the time series after the pre-processing
    Returns:
    - data (array-like): array containing the time series with or without differiantiation.
    """
    if not stationarity_flag:
        # print('time series was not stationary, it has been differienciated')
        data = data.diff().dropna()
    # else:
    #     print('no need to differienciate')
    return data


def compute_significant_positive_lags(
        acf_values,
        confint,
        ):
    """This fucntion computes the significant lags after centering them respect to the acf value.
    Arguments:
        - acf_values (array): array containing the acf values computed from sm.tsa.acf fucntion;
        - confint (array of lists): array containing the confidence interval for each acf value [lower bound, upper bound]
    Returns:
    - significant lags (list): lags where ACF values are outside the confidence intervals, so considered significant
    - centered_ci (array(list)): confidence intervals centered around 0
    """
    # Recenter CI, necessary to have the confidence intervals centered to zero (the confint are centered around the ACF value)
    centered_ci = confint - acf_values[:, None]

    # Find the significant lags where ACF values are outside the confidence intervals
    # significant_lags = np.where((acf_values < centered_ci[:, 0]) | (acf_values > centered_ci[:, 1]))[0] # keep all significant peaks
    significant_lags = np.where(acf_values > centered_ci[:, 1])[0] # keep only positive peaks
    # print("Significant lags:", significant_lags)
    return significant_lags, centered_ci


def plot_acf_and_significant_lags(
        input_data,
        input_name,
        image_path,
        acf_values,
        significant_lags,
        plotted_lags=6000,
        alpha=0.05,
        ):
        """Plot ACF and in red the significant lags and values
        Arguments:
                - acf_values (array): array with the autocorrelation values computed from sm.tsa.acf fucntion
                - significant lags (list): list of significant lags where ACF values are outside the confidence intervals
                - lags (int): number of lags to plot
                - alpha (float): confidence interval. If alpha=.05, 95 % confidence intervals are returned
                - barlett_confint (bool): if True it computes the confindence interval using the Barlett's formula, otherwise it uses a constant range of 1.96 / sqrt (N)
        Returns:
                - Correlogram: ACF values as function of the lags. The blue region is the confidence interval. Positive values outside this range are considered to be significant and outlined in red.
        """

        # Plot the ACF with confidence intervals
        fig, ax = plt.subplots()
        plot_acf(input_data,
                ax=ax,
                lags=6000,
                alpha=alpha,
                bartlett_confint=True)

        # Mark significant lags with red circles
        # Select only significant lags within the plotted lags interval
        significant_lags = significant_lags[significant_lags <= plotted_lags]
        ax.scatter(significant_lags, acf_values[significant_lags], color='r', marker='o')
        plt.xlabel("Lag")
        plt.ylabel("ACF Value")
        plt.title(input_name)
        # plt.show()
        # Save plots in the folder= 
        save_path = image_path + '/ACF_plots/'
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(image_path + '/ACF_plots/' + input_name)
        # plt.close(fig)


def find_lag_threshold(
        acf_values,
        centered_ci
        ):
    """
    Automatically find the lag threshold where ACF values fall below a certain percentage of the initial peak.
    Arguments:
        acf_values (array): Array of ACF values.
        decay_percent (float): Percentage of the initial peak to define the threshold.
    Returns:
        lag_threshold (int): The lag threshold where the ACF values fall below the specified percentage.
    """
    first_decay_threshold = np.where((abs(acf_values) < centered_ci[:, 1]))
    # print(f"First decay lag threshold: {first_decay_threshold[0][0]}")
    return first_decay_threshold[0][0]


def find_groups_of_lags(filtered_significant_lags):
    """This function finds different groups of lags among the significant one. The goal is to use it to find local maxima in each group.
    Arg:
        filtered_significant_lags (List): list containing the significant lag after filtering out the first decay
    Returns:
        lag_groups (List(Tuples)): list of tuples, first value is the group number (int) and the second is a list of lags belongiing to this group.
    """
    g = 0
    lag_groups= []
    l_list = []
    for i, l in enumerate(filtered_significant_lags):
        # Add first element to the first list
        if i == 0:
            l_list.append(l)
        # Add elements if lag are consecutive
        elif l == filtered_significant_lags[i-1] + 1: 
            l_list.append(l)
        # If lags are not consecutive
        else:
            # Save previous group of lags
            lag_group = (g, l_list)
            lag_groups.append(lag_group)
            # Create a new group
            g += 1
            l_list = [l]
    # Save last group of lags
    if l_list:
        lag_group = (g, l_list)
        lag_groups.append(lag_group)
    # # Print groups of lags
    # for group in lag_groups:
    #     print(group)
    return lag_groups


def compute_fundamental_interval_with_decay_threshold(
        acf_values,
        centered_ci,
        significant_lags,
        lag_threshold=None,
        sample_spacing=0.097, # inverse of sampling rate (sampling frequency)
        ):
    """
    This function finds the fundamental period among the significant lags.
    Arguments:
        - acf_values (array): Array of ACF values.
        - centered_ci (array): Array of centered confidence intervals.
        - significant_lags (list): List of significant lags.
        - lag_threshold (int): Minimum lag to consider for periodicity.
        - sample_spacing (float): sampling frequency of the signal, default is 1s
    Returns:
        fundamental_interval (int): List of tuples with value of the fundamental interval in seconds and respecive ACF value,
        sorted iin descending order accordingly to ACF.
    """
    if lag_threshold is None:
        lag_threshold = find_lag_threshold(acf_values, centered_ci)

    # Filter significant lags to ignore initial lags below the threshold
    filtered_significant_lags = [lag for lag in significant_lags if lag > lag_threshold]

    # Create groups of significant lags
    lag_groups = find_groups_of_lags(filtered_significant_lags)
    fundamental_lags = []
    for group in lag_groups:
        print(group)
        # Create list of tuples with significant lag and corresponding acf value
        # significant_tuples = [(lag, acf_values[lag]) for lag in filtered_significant_lags]
        significant_tuples = [(lag, acf_values[lag]) for lag in group[1]]

        # Sort the selected lags and corresponding acf values by ACF value in descending order
        sorted_significant_tuples = sorted(significant_tuples, key=lambda x: x[1], reverse=True)
        print(sorted_significant_tuples)
        # Check if there are enough significant lags to determine the fundamental period
        if len(sorted_significant_tuples) > 1:
            # Select the second highest significant acf value (ignoring the first because it's always 1)
            if sorted_significant_tuples[0][0] == 0:
                fundamental_lag = sorted_significant_tuples[1][0]
            else:
                fundamental_lag = sorted_significant_tuples[0][0]
                fundamental_acf = sorted_significant_tuples[0][1]

            print(f"The selected lag of this signal is: {fundamental_lag}")
            print(f"The fundamental interval of this signal is: {fundamental_lag * sample_spacing}s")
            fundamental_lags.append((np.round(fundamental_lag * sample_spacing, 3), np.round(fundamental_acf, 3)))
        else:
            print("Not enough significant lags beyond the initial decay to determine the fundamental period.")
            fundamental_lags = None
    sorted_fundamental_lag = sorted(fundamental_lags, key=lambda x: x[1], reverse=True)
    print('Sorted_list: ', sorted_fundamental_lag)
    return sorted_fundamental_lag
