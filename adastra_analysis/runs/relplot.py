from adastra_analysis.common.dataset import Dataset
from adastra_analysis.common.run import Run

from adastra_analysis.runs.util import relplot_utils


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
            y_col = self.relplot_args['y']
            _data = relplot_utils.remove_outliers(_data, y_col)

        # Establish and build the figure.
        fig = relplot_utils.build_seaborn_relplot(
            data=_data,
            relplot_args=self.relplot_args,
            figsize=self.figsize,
            title=self.title,
            style=self.style,
            axhline=self.axhline,
        )

        return fig


    def save(self, result):
        """
        Write the plot out as a PNG file.
        """
        self.prepare_directories(self.file)
        result.savefig(self.file, bbox_inches='tight')
    
        # Reset the environment (Pyplot is memory-hungry).
        relplot_utils.reset_pyplot()
