from classes.dataset import Dataset

from util.utils import prepare_directories


class Query:
    """
​
    """
    def __init__(
        self,

        adastra_dataset,
        dataset_alias,
        sql,
        where=None,
        datasets=None,
    ):
        self.query = (
            Dataset(adastra_dataset)
                .filter_where(where)
                .query_sql(sql, dataset_alias, datasets)
        )


    @staticmethod
    def query_constructor(loader, node):
        return Query(**loader.construct_mapping(node))


    def get(self):
        """
        Exit the Dataset.
        """
        return self.query


    # Functions to write the Dataset in different formats.
    def to_disk(self, filepath):
        """
        Write the dataset as JSON lines.
        """
        prepare_directories(filepath)
        self.query.to_json(filepath, orient='records', lines=True)
