import seaborn as sns
import matplotlib.pyplot as plt


def plot_boxplots(data_df, input_feature, axis, palette='tab10'):
    """This function plots the boxplot of the features of interest, for the three different classes.
    data_df = dataframe with all the data and the features - called df_total in the main
    input_feature = a string with the name of feature respect to which the box plot will be shown
    axis = the axis for the subplot
    palette = string with a palette, choose between default tab10 or flare"""

    sns.boxplot(data=data_df, x='Class', y=input_feature, ax=axis, orient='v', palette=palette).set(title=input_feature)
    if input_feature == 'Contraction power':
        axis.set(ylabel='Contraction power [\u03BCm^2 / s]')
    elif input_feature in ['Standard_deviation', 'Mean', 'Quantile_75']:
        axis.set(ylabel=input_feature+' [\u03BCm]')
    else:
        axis.set(ylabel=input_feature)
