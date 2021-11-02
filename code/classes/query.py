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


    def build(self, datasets):
        """
        
        """
        return Dataset(**self.dataset).build_dataset(datasets=datasets)


    def save(self, result):
        """
        
        """
        self.prepare_directories(self.file)
        Dataset.to_disk(result, self.file)
