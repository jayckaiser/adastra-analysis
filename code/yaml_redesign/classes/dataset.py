from os import stat
import sys

import pandas as pd
import pandasql as psql

from utils.utils import prepare_directories


class DataLake:
    """
    A collection of Datasets.
    """
    def __init__(
        self,
        data_lake=None,
    ):
        if data_lake:
            self.data_lake = data_lake
        else:
            self.data_lake = {}

    
    def add_dataset(
        self,

        name,
        file=None,
        dataset=None,
    ):
        """
        
        """
        # 
        if dataset:
            _dataset = Dataset(**dataset)

            if file:
                _dataset.to_disk(file)

        # 
        elif file:
            _dataset = Dataset.load_dataset(file)

        # 
        elif name in self.data_lake:
            _dataset = self.data_lake.get(name)
        else:
            print("#> A dataset needs a `file` or `dataset` specified!")
            sys.exit()

        # 
        self.data_lake[name] = _dataset


    def get(self, name):
        """
        
        """
        if name not in self.data_lake:
            print(f"`! Dataset {name}` undefined!")
            sys.exit(0)
        else:
            return self.data_lake.get('name')



    def filter_datasets(self, filters):
        """
        
        """
        if filters:
            for filter in filters:
                name = filters['name']
                where = filters['where']

                _dataset = self.get(name)
                _dataset = _dataset.filter_where(where)

                self.data_lake[name] = _dataset


    def query_sql(self, sql):
        """
        
        """
        for name, dataset in self.data_lake.items():
                exec(f"{name} = dataset.copy()")

        _data = psql.sqldf(sql)

        return Dataset(_data)



    def copy(self):
        """
        
        """
        return {
            key: data.copy() for key, data in self.data_lake.items()
        }
                




class Dataset:
    """
    Extension of pandas DataFrame for interfacing with SQL commands.
    """
    def __init__(
        self,

        data,
        columns=None,
    ):
        self.dataset = self.build_dataset(data, columns)


    @classmethod
    def load_dataset(self, file):
        """
        
        """
        _dataframe = pd.read_json(
            file,
            orient='records',
            lines=True
        )
        return Dataset(_dataframe)



    @staticmethod
    def build_dataset(data, columns=None):

        # Dataset or DataFrame is given.
        if isinstance(data, Dataset) or isinstance(data, pd.DataFrame):
            return data
        
        # Dictionary and column names are given.
        else: 
            return pd.Dataframe(data, columns=columns)


    def get(self):
        return self.dataset.copy()
    
    
    def filter_where(self, where_clauses):
        """
        Apply one or more where-clauses to the dataset, using the alias provided in the PandaSQL query.
        """
        _data = self.get()

        if where_clauses:
            
            # Allow either a str or List[str].
            if isinstance(where_clauses, str):
                filters = [where_clauses]
            
            for where_clause in filters:

                _data = psql.sqldf(f"""
                    select * from _data
                    where {where_clause}
                """)

        self.dataset = Dataset(_data)
