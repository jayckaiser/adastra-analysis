import gc

import numpy as np
import pandas as pd
from scipy import stats

import matplotlib.pyplot as plt
import seaborn as sns

from utils.utils import prepare_directories


class Relplot:
    """
    This is a class to simplify creating Relplots and outputting to disk.
    """
    def __init__(
        self,
        dataset,
        relplot_args,
        figsize=None,
        axhline=None,
        remove_outliers=False,
    ):
        self.relplot = self.build_figure(
            data=dataset,
            relplot_args=relplot_args,
            figsize=figsize,
            axhline=axhline,
            remove_outliers=remove_outliers,
        )
    


    @staticmethod
    def build_figure(
        data, relplot_args,
        figsize=None, axhline=None,
        remove_outliers=False,
    ):
        """
        Standardized method to build a Seaborn figure.
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

        fig = plt.gcf()
        fig.set_size_inches(*figsize)

        return fig

    

    def to_disk(self, filepath):
        """
        Save the relplot as a file, then reset pyplot.

        (Pyplot is rude and loves to hold onto memory.)
        """
        prepare_directories(filepath)
        self.relplot.savefig(filepath, bbox_inches='tight')
        
        # 
        plt.close('all')
        gc.collect()

