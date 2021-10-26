import gc
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from scipy import stats

from classes.dataset import Dataset
from util.utils import prepare_directories


class Relplot:
    """
​
    """
    def __init__(
        self,

        data,
        columns=None,
        where=None,
        sql=None,
        dataset_alias=None,
        datasets=None,

        relplot_args=None,
        figsize=(16,10),
        style="darkgrid",
        title=None,
        axhline=None,
        remove_outliers=False,
    ):
        # Relplots are really graphical extensions of Datasets.
        self.data = Dataset(
            data,
            columns=columns,
            where=where,
            sql=sql,
            dataset_alias=dataset_alias,
            datasets=datasets,
        ).get_data()

        # 
        self.relplot = self.build_relplot(
            self.data,
            relplot_args=relplot_args,

            figsize=figsize,
            style=style,
            title=title,
            axhline=axhline,
            remove_outliers=remove_outliers,
        )


    @staticmethod
    def relplot_constructor(loader, node):
        return Relplot(**loader.construct_mapping(node))


    @staticmethod    
    def build_relplot(
        data,
        relplot_args,

        figsize,
        style,
        title,
        axhline,
        remove_outliers,
    ):
        """
        Standardized method to build a Seaborn relplot.
        """
        _data = data.copy()

        # Remove outliers if option marked.
        if remove_outliers:
            y = relplot_args['y']
            _data = _data[
                (np.abs(stats.zscore(_data[y])) < 3)
            ]

        # Establish and build the figure.
        plt.figure()
        sns.relplot(data=_data, **relplot_args)

        # Set the style if specified (defaults to 'darkgrid' such that Cassius can be seen).
        sns.set_theme(style=style)

        # Add a title if specified.
        plt.title(title)

        # Add a custom horizontal line if specified.
        plt.axhline(axhline, linestyle='--', color='black', alpha=0.5)

        # Set the output size and return.
        fig = plt.gcf()
        fig.set_size_inches(*figsize)

        return fig


    def to_disk(self, filepath):
        """
        Write the plot out as a PNG file.
        """
        prepare_directories(filepath)
        self.relplot.savefig(filepath, bbox_inches='tight')
    
        # Reset the environment (Pyplot is memory-hungry).
        plt.close('all')
        gc.collect()
