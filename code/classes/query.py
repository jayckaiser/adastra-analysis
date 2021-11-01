from classes.dataset import Dataset

class Query:
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
        

    @staticmethod
    def query_constructor(loader, node):
        return Query(**loader.construct_mapping(node))


    def build_query(self, datasets):
        """
        
        """
        self.result =  Dataset(**self.dataset).build_dataset(datasets=datasets)


    def to_disk(self, file=None):
        """
        
        """
        file = file or self.file

        prepare_directories(file)
        Dataset.to_disk(self.result, file)
