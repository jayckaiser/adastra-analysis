import numpy as np
import pandas as pd
from scipy import stats

import matplotlib.pyplot as plt
import seaborn as sns


def build_dataset(dataset_params):
    """
    Standardized method to build helper tables.
    """
    columns = dataset_params['columns']
    data    = dataset_params['data']

    return pd.DataFrame(list(data.items()), columns=columns)


def build_figure(data, figsize, axhline, remove_outliers, **kwargs):
    """
    Standardized method to build a Seaborn figure.
    """
    # Establish the size of the figure.
    if figsize is None:
        figsize = (16,10)

    # Remove outliers if option marked.
    if remove_outliers:
        y = kwargs['y']
        data = data[
            (np.abs(stats.zscore(data[y])) < 3)
        ]

    # Set to darkgrid (to see Cassius).
    sns.set_theme(style='darkgrid')

    plt.figure()
    sns.relplot(
        data=data,
        **kwargs
    )

     # Add a custom horizontal line if specified.
    if axhline is not None:
        plt.axhline(axhline, linestyle='--', color='black', alpha=0.5)

    fig = plt.gcf()
    fig.set_size_inches(*figsize)

    return fig
