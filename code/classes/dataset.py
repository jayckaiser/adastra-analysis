import sys

import pandas as pd
import pandasql as psql

from classes.run import Run


class Dataset(Run):
    """
    Extension of pandas DataFrame for interfacing with SQL commands.
    """
    def __init__(
        self,

        name: str = None,
        file: str = None,
        sql : str = None,
        filters: list = None,
        dataset_args: dict = None,
    ):
        self.name = name
        self.file = file
        self.sql  = sql
        self.filters = filters
        self.dataset_args = dataset_args

        self.result = None


    def build_dataset(self, datasets):
        """
        Note: This relies on Python passing the same `datasets` around in memory.
        """

        _datasets = datasets.copy()

        # OPTIONAL: Filter the datasets before creating this one.
        if self.filters and self.sql:
            _datasets = Dataset.filter_datasets(self.filters, _datasets)

        # REQUIRED
        if self.dataset_args:
            dataset = Dataset.data_to_dataset(**self.dataset_args)
        elif self.file:
            dataset = Dataset.load_dataset(self.file)
        elif self.sql:
            dataset = Dataset.query_datasets(self.sql, _datasets)
        elif self.name:
            dataset = datasets.get(self.name)
            if dataset is None:
                print(f"! No dataset logic defined! Dataset `{self.name}` has not been defined yet!")
        else:
            print("! No dataset logic defined! Provide `dataset_args` or `sql` to a dataset!")
            sys.exit(0)

        #  # OPTIONAL: Save or alias the dataset.
        # if self.file and (self.dataset_args or self.sql):
        #     self.to_disk(self.file)

        if self.name:
            datasets[self.name] = dataset

        self.result = dataset
        return dataset


    ###
    @staticmethod
    def filter_datasets(filters, datasets):
        """
        
        """
        # 
        _datasets = datasets.copy()
        
        for filter in filters:
            name = filter['name']
            where = filter['where']

            dataset = _datasets.get(name)
            dataset = Dataset.filter_where(dataset, where)

            _datasets[name] = dataset

        return _datasets


    @staticmethod
    def query_datasets(sql, datasets):
        """
        
        """
        for name, _dataset in datasets.items():
            exec(f"{name} = _dataset")

        return psql.sqldf(sql)


    ### 
    @staticmethod
    def data_to_dataset(data, columns=None):
        """
        
        """
        # Dataset or DataFrame is given.
        if isinstance(data, pd.DataFrame):
            return data
        
        # Dictionary and column names are given.
        else: 
            return pd.DataFrame(data.items(), columns=columns)


    @staticmethod
    def load_dataset(file):
        """
        
        """
        return pd.read_json(
            file,
            orient='records',
            lines=True
        )


    @staticmethod
    def filter_where(dataset, where_clause):
        """
        Apply one or more where-clauses to the dataset, using the alias provided in the PandaSQL query.
        """
        _dataset = dataset.copy()

        if where_clause:
            
            # Allow either a str or List[str].
            _dataset = psql.sqldf(f"""
                select * from _dataset
                where {where_clause}
            """)
    
        return _dataset


    @staticmethod
    def to_disk(dataset, file, info=False):
        """
        Write the dataset as JSON lines.
        """
        Run.prepare_directories(file)

        dataset.to_json(file, orient='records', lines=True)
        
        if info:
            print(f"* Dataset saved: {file}")
