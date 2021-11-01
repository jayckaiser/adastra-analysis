from classes.dataset import Dataset
from classes.run import Run


class Query(Run):
    """
​
    """
    def __init__(
        self,

        name,
        file,
        dataset,
    ):

        self.name = name
        self.file = file
        self.dataset = dataset

        self.result = None


    def build_query(self, datasets):
        """
        
        """
        self.result =  Dataset(**self.dataset).build_dataset(datasets=datasets)


    def to_disk(self, file=None):
        """
        
        """
        file = file or self.file

        self.prepare_directories(file)
        Dataset.to_disk(self.result, file)
