import gc
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from scipy import stats

from classes.dataset import Dataset
from classes.run import Run


class Relplot(Run):
    """
​
    """
    def __init__(
        self,

        name,
        file,
        dataset,

        relplot_args=None,
        figsize=(16,10),
        style="darkgrid",
        title=None,
        axhline=None,
        remove_outliers=False,
    ):
        self.name = name
        self.file = file
        self.dataset = dataset

        self.relplot_args = relplot_args
        self.figsize = figsize
        self.style = style
        self.title = title
        self.axhline = axhline
        self.remove_outliers = remove_outliers


    def build(self, datasets):
        """
        Standardized method to build a Seaborn relplot.
        """
        _data = Dataset(**self.dataset).build_dataset(datasets=datasets)

        # Remove outliers if option marked.
        if self.remove_outliers:
            y = self.relplot_args['y']
            _data = _data[
                (np.abs(stats.zscore(_data[y])) < 3)
            ]

        # Establish and build the figure.
        plt.figure()
        sns.relplot(data=_data, **self.relplot_args)

        # Set the style if specified (defaults to 'darkgrid' such that Cassius can be seen).
        sns.set_theme(style=self.style)

        # Add a title if specified.
        plt.title(self.title)

        # Add a custom horizontal line if specified.
        if self.axhline:
            plt.axhline(self.axhline, linestyle='--', color='black', alpha=0.5)

        # Set the output size and return.
        fig = plt.gcf()
        fig.set_size_inches(*self.figsize)

        return fig


    def save(self, result):
        """
        Write the plot out as a PNG file.
        """
        self.prepare_directories(self.file)
        result.savefig(self.file, bbox_inches='tight')
    
        # Reset the environment (Pyplot is memory-hungry).
        plt.close('all')
        gc.collect()
