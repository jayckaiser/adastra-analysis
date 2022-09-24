import os

from src.common.dataset import Dataset
from src.common.run import Run

from src.runs.util import screenplay_utils


class Screenplay(Run):
    """
​
    """
    def __init__(
        self,

        name,
        folder, 
        dataset,

        justify,
        line_sep,
        file_col,
        screenplay_col,
        contexts,

    ):
        self.name = name
        self.folder = folder
        self.dataset = dataset

        self.justify = justify
        self.line_sep = line_sep
        self.file_col = file_col
        self.screenplay_col = screenplay_col
        self.contexts = contexts


    def build(self, datasets):
        """
        
        """
        _data = Dataset(**self.dataset).build_dataset(datasets=datasets)


        # For each format, subset the dataframe and format each line.
        for context_config in self.contexts:

            _data = screenplay_utils.apply_screenplay_context(
                _data,
                context_config,
                screenplay_col=self.screenplay_col,
                justify=self.justify,
            )

        return _data


    def save(self, result):
        """
        Screenplays differ from other Runs.
        They are written out to a folder as many files.
        
        `file_col` determines how to divide the files.
        (i.e. `file` for acts, `speaker` for monologues, etc.)
        """
        # Iterate the file names and output each as a separate file.
        for file in result[self.file_col].unique():
            where = f'{self.file_col} = "{file}"'

            file_data = Dataset.filter_where(result, where)
            file_lines = file_data[self.screenplay_col].tolist()

            file_path = os.path.join(self.folder, file + '.txt')
            self.prepare_directories(file_path)
            with open(file_path, 'w') as fp:
                fp.write(
                    self.line_sep.join(file_lines)
                )
