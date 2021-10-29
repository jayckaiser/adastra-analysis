from os import stat
import sys

import pandas as pd
import pandasql as psql

from utils.utils import prepare_directories


class Dataset:
    """
    Extension of pandas DataFrame for interfacing with SQL commands.
    """
    def __init__(
        self,
        datasets: dict = {},

        name: str = None,
        file: str = None,
        sql : str = None,
        filters: list = None,
        dataset_args: dict = None,
    ):
        self.datasets = datasets.deepcopy()

        # OPTIONAL: Filter the datasets before creating this one.
        if filters:
            self.filter_datasets(filters)

        # REQUIRED
        if file and not (dataset_args or sql):
            dataset = Dataset.load_dataset(file)
        elif dataset_args:
            dataset = Dataset.build_dataset(**dataset_args)
        elif sql:
            dataset = self.query_datasets(sql)
        else:
            print("! No dataset logic defined! Provide `dataset_args` or `sql` to a dataset!")

         # OPTIONAL: Save or alias the dataset.
        if file and (dataset_args or sql):
            Dataset.to_disk(dataset, file)

        if name:
            self.datasets[name] = dataset

        return self.datasets


    def get(self, key):
        """
        
        """
        if key in self.datasets:
            return self.datasts[key]
        else:
            print(f"! Dataset `{key}` not found in datasets!")


    ###
    def filter_datasets(self, filters):
        """
        
        """
        if filters is None:
            return self.datasets

        # 
        _datasets = self.datasets.deepcopy()
        
        for filter in filters:
            name = filter['name']
            where = filter['where']

            dataset = self.get(name)
            dataset = Dataset.filter_where(dataset, where)

            _datasets[name] = dataset

        self.datasets = _datasets


    def query_datasets(self, sql_query):
        """
        
        """
        for name, _dataset in self.datasets.items():
            exec(f"{name} = _dataset")

        return psql.sqldf(sql_query)



    ### 
    @staticmethod
    def build_dataset(data, columns=None):
        """
        
        """
        # Dataset or DataFrame is given.
        if isinstance(data, pd.DataFrame):
            return data
        
        # Dictionary and column names are given.
        else: 
            return pd.Dataframe(data, columns=columns)


    @staticmethod
    def load_dataset(file):
        """
        
        """
        _dataframe = pd.read_json(
            file,
            orient='records',
            lines=True
        )
        return _dataframe


    @staticmethod
    def filter_where(dataset, where_clause):
        """
        Apply one or more where-clauses to the dataset, using the alias provided in the PandaSQL query.
        """
        _dataset = dataset.copy()

        if where_clause:
            
            # Allow either a str or List[str].
            _dataset = psql.sqldf(f"""
                select * from _data
                where {where_clause}
            """)
    
        return _dataset


    @staticmethod
    def to_disk(dataset, path):
        """
        Write the dataset as JSON lines.
        """
        prepare_directories(path)
        dataset.to_json(path, orient='records', lines=True)

