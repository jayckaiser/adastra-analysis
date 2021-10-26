from classes.dataset import Dataset

from util.utils import prepare_directories


class Query:
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
    ):
        self.data = Dataset(
            data,
            columns=columns,
            where=where,
            sql=sql,
            dataset_alias=dataset_alias,
            datasets=datasets,
        ).get_data()


    @staticmethod
    def query_constructor(loader, node):
        return Query(**loader.construct_mapping(node))


    # Functions to write the Dataset in different formats.
    def to_disk(self, filepath):
        """
        Write the dataset as JSON lines.
        """
        prepare_directories(filepath)
        self.data.to_json(filepath, orient='records', lines=True)
