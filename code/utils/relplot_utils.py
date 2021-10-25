import gc

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib.pyplot as plt
import seaborn as sns

from utils.utils import prepare_directories


def build_relplot(
    data, relplot_args,
    title=None,
    figsize=None, axhline=None,
    remove_outliers=False,
):
    """
    Standardized method to build a Seaborn relplot.
    """
    # 
    data = data.copy()

    # Establish the size of the figure.
    if figsize is None:
        figsize = (16,10)

    # Remove outliers if option marked.
    if remove_outliers:
        y = relplot_args['y']
        data = data[
            (np.abs(stats.zscore(data[y])) < 3)
        ]

    # Set to darkgrid (to see Cassius).
    sns.set_theme(style='darkgrid')

    plt.figure()
    sns.relplot(data=data, **relplot_args)

    # Add a custom horizontal line if specified.
    if axhline is not None:
        plt.axhline(axhline, linestyle='--', color='black', alpha=0.5)

    # Add a title if defined.
    if title is not None:
        plt.title(title)

    fig = plt.gcf()
    fig.set_size_inches(*figsize)

    return fig

    

def relplot_to_disk(relplot, filepath):
    """
    Save the relplot as a file, then reset pyplot.

    (Pyplot is rude and loves to hold onto memory.)
    """
    prepare_directories(filepath)
    relplot.savefig(filepath, bbox_inches='tight')
    
    # 
    plt.close('all')
    gc.collect()
