import glob
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pre_processing import process_single_ts
from feature_extraction import create_feature_in_dataframe
from plot_boxplot import plot_boxplots

folder_path_old = '/Users/donatella.cea/Documents/Contraction analysis of neuromuscular organoids/data/' \
                  'final_first_set_of_data'
figure_path = '/Users/donatella.cea/Documents/Contraction analysis of neuromuscular organoids/figure_test/'
data = {'curare': [],
        'Weak': [],
        'Strong': []}
for filename in glob.glob(os.path.join(folder_path_old, '*.npy')):
    for key in data.keys():
        if key in filename:
            with open(filename, 'r') as f:
                data[key].append([os.path.split(filename)[-1],
                                  np.load(filename)])
            break

folder_path_new = '/Users/donatella.cea/Documents/Contraction analysis of neuromuscular organoids/data/' \
                  'final_second_set_of_data'

for filename in glob.glob(os.path.join(folder_path_new, '*.npy')):
    with open(filename, 'r') as f:
        data['curare'].append([os.path.split(filename)[-1],
                               np.load(filename)])

data['Weak'][4][1] = data['Weak'][4][1][:, :650]

# Pre-processing
data_processed = {'curare': [],
                  'Weak': [],
                  'Strong': []}
for key in data.keys():
    for data_k in data[key]:
        data_processed[key].append([data_k[0], process_single_ts(data_k[1])])

# Plot time series
t_weak = 0.5
t_conversion = 0.097
plot_info = {'curare': {'y_min': -2.5, 'y_max': 2.5,
                        'subplot_layout_row': 7, 'subplot_layout_col': 2,
                        'title': 'No contraction - curare'},
             'Weak': {'y_min': -2.5, 'y_max': 2.5,
                      'subplot_layout_row': 5, 'subplot_layout_col': 1,
                      'title': 'Weak contraction'},
             'Strong': {'y_min': -20, 'y_max': 20,
                        'subplot_layout_row': 5, 'subplot_layout_col': 1,
                        'title': 'Strong Contraction'}}

colors = ["#43C6DB", "#93FFE8", "dodgerblue", "mediumseagreen", "slateblue", "#737CA1", "#29465B", "#368BC1",
          "#AFDCEC", "#66CDAA"]
for key in data_processed.keys():
    fig, axis = plt.subplots(plot_info[key]['subplot_layout_row'], plot_info[key]['subplot_layout_col'],
                             figsize=(15, 10))
    fig.suptitle(plot_info[key]['title'], fontsize=16)
    plt.tight_layout()
    for ax, data_i in zip(axis.flat, data_processed[key]):
        for i in range(data_i[1].shape[0]):
            ax.plot([t * t_conversion for t in range(len(data_i[1][i, :]))], data_i[1][i, :],
                    color=colors[i], alpha=0.5)
            # ax.plot(data_i[1][i, :], color=colors[i], alpha=0.5)
        ax.set_title(data_i[0], y=1.0, pad=-14)
        ax.set_xlabel('Time [s]')
        ax.set_ylabel('y [\u03BCm]')
        ax.set_ylim(plot_info[key]['y_min'], plot_info[key]['y_max'])
        ax.axhline(y=t_weak, color='g', linestyle='--', label='std')
        ax.axhline(y=-t_weak, color='g', linestyle='--', label='std')
    fig.savefig(figure_path + plot_info[key]['title'])


# Compute features and create dataframes for all classes combinations
# 3 Classes
df_data = pd.DataFrame()
for cls, key in enumerate(data_processed.keys()):
    print(cls, key)
    df_key = create_feature_in_dataframe(data_processed[key], cls)
    df_data = pd.concat([df_data, df_key], axis=0, ignore_index=True)
    # for data_k in data[key]:
    #     df_data = create_feature_in_dataframe(data_k, cls)
print(df_data)
# 2 Classes: curare vs weak + strong
df_data_2_classes = df_data.copy()
df_data_2_classes.loc[df_data_2_classes['Class'] >= 2, 'Class'] = 1
# 2 Classes  - no weak
df_data_no_weak = df_data.copy()
df_data_no_weak = df_data_no_weak[df_data_no_weak.Class != 1]
# 2 Classes - no strong
df_data_no_strong = df_data.copy()
df_data_no_strong = df_data_no_strong[df_data_no_strong.Class != 2]

# Box plot for each feature
boxplot_info = {'3_classes': {'data': df_data,
                              'palette': ['royalblue', 'darkorange', 'seagreen'],
                              'title': 'Uni-variate analysis - 3 classes'},
                '2_classes': {'data': df_data_2_classes,
                              'palette': ['royalblue', 'palevioletred'],
                              'title': 'Uni-variate analysis - 2 classes'},
                'no_weak': {'data': df_data_no_weak,
                            'palette': ['royalblue', 'seagreen'],
                            'title': 'Uni-variate analysis - 2 classes - no weak'},
                'no_strong': {'data': df_data_no_strong,
                              'palette': ['royalblue', 'darkorange'],
                              'title': 'Uni-variate analysis - 2 classes - no strong'}
                }
for key in boxplot_info.keys():
    fig, axis = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle(boxplot_info[key]['title'], fontsize=16)
    for col, ax in zip(list(df_data.columns)[2:-1], axis.ravel()):
        plot_boxplots(boxplot_info[key]['data'], col, ax, palette=boxplot_info[key]['palette'])
    fig.tight_layout()
    fig.savefig(figure_path + boxplot_info[key]['title'])

# Plot 2D
bi_variate_plot_info = {'3_classes': {'data': df_data,
                                      'palette': ['royalblue', 'darkorange', 'seagreen'],
                                      'title': 'Bi-variate analysis - 3 classes'},
                        '2_classes': {'data': df_data_2_classes,
                                      'palette': ['royalblue', 'palevioletred'],
                                      'title': 'Bi-variate analysis - 2 classes'},
                        'no_weak': {'data': df_data_no_weak,
                                    'palette': ['royalblue', 'seagreen'],
                                    'title': 'Bi-variate analysis - 2 classes - no weak'},
                        'no_strong': {'data': df_data_no_strong,
                                      'palette': ['royalblue', 'darkorange'],
                                      'title': 'Bi-variate analysis - 2 classes - no strong'}
                        }
var_plot = [
    ['Energy', '%_of_absolute_sum_of_changes', [0, 0]],
    ['Energy', 'Quantile_75', [0, 1]],
    ['%_of_count_above_threshold', '%_of_absolute_sum_of_changes', [0, 2]],
    ['%_of_absolute_sum_of_changes', 'Quantile_75', [1, 0]],
    ['%_of_absolute_sum_of_changes', 'Standard_deviation', [1, 1]],
    ['Quantile_75', 'Standard_deviation', [1, 2]]
]

for key in boxplot_info.keys():
    fig_bi, axis = plt.subplots(2, 3, figsize=(15, 8))
    fig_bi.suptitle(bi_variate_plot_info[key]['title'], fontsize=16)
    for x, y, ax in var_plot:
        sns.scatterplot(data=bi_variate_plot_info[key]['data'],
                        x=x, y=y, hue='Class',
                        palette=bi_variate_plot_info[key]['palette'], ax=axis[ax[0], ax[1]])
    fig_bi.tight_layout()
    fig_bi.savefig(figure_path + bi_variate_plot_info[key]['title'])

plt.show()
