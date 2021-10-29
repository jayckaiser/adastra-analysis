from classes.dataset import Dataset

from util.utils import prepare_directories


class Query:
    """
​
    """
    def __init__(
        self,
        datasets,

        name,
        file,
        dataset,
    ):
        self.datasets = datasets

        self.name = name
        self.file = file
        self.dataset = dataset

        self.run_query()


    @staticmethod
    def query_constructor(loader, node):
        return Query(**loader.construct_mapping(node))


    def run_query(self):
        """
        
        """
        try:
            data = Dataset(datasets = self.datasets, **self.dataset)
            Dataset.to_disk(data, self.file)

            print(f"* Query `{self.name}` completed: {self.file}")

        except Exception as err:
            print(f"! Query `{self.name}` failed: {err}")
