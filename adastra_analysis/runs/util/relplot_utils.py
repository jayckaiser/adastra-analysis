import gc
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from scipy import stats


def remove_outliers(data, col, sigma=3):
    """
    
    """
    return data[
        (np.abs(stats.zscore(data[col])) < sigma)
    ]


def build_seaborn_relplot(
    data,
    relplot_args,
    figsize,
    title,
    style,
    axhline,
):
    """
    
    """
    # Establish and build the figure.
    plt.figure()
    sns.relplot(data=data, **relplot_args)

    # Set the style if specified (defaults to 'darkgrid' such that Cassius can be seen).
    sns.set_theme(style=style)

    # Add a title if specified.
    plt.title(title)

    # Add a custom horizontal line if specified.
    if axhline:
        plt.axhline(axhline, linestyle='--', color='black', alpha=0.5)

    # Set the output size and return.
    fig = plt.gcf()
    fig.set_size_inches(*figsize)

    return fig


def reset_pyplot():
    """
    
    """
    plt.close('all')
    gc.collect()