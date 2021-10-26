import pandas as pd
import pandasql as psql

from utils.utils import prepare_directories


class Dataset:
    """
    Extension of pandas DataFrame for interfacing with SQL commands.
    """
    def __init__(self, data, columns=None):
        self.data = self.prepare_dataset(data, columns=columns)


    @staticmethod
    def prepare_dataset(data, columns=None):
        """
        Create the DataFrame, depending on type of input.
        """

        # Dataset or DataFrame is given.
        if isinstance(data, Dataset) or isinstance(data, pd.DataFrame):
            return data
        
        # Local filepath is given.
        elif isinstance(data, str):
            return pd.read_json(
                data,
                orient='records',
                lines=True
            )
        
        # Dictionary and column names are given.
        else: 
            return pd.Dataframe(data, columns=columns)

    
    def query_sql(self, sql_query, alias, datasets=None):
        """
        
        """
        exec(f"{alias} = self.data.copy()")

        if datasets:
            for dataset_name, dataset in datasets.items():
                exec(f"{dataset_name} = dataset.copy()")

        _data = psql.sqldf(sql_query)

        self.data = _data


    def filter_where(self, where_clauses):
        """
        Apply one or more where-clauses to the dataset, using the alias provided in the PandaSQL query.
        """
        _data = self.data.copy()

        if where_clauses:
            
            # Allow either a str or List[str].
            if isinstance(where_clauses, str):
                filters = [where_clauses]
            
            for where_clause in filters:

                _data = psql.sqldf(f"""
                    select * from _data
                    where {where_clause}
                """)

        self.data = _data


    def get(self):
        """
        Exit the Dataset.
        """
        return self.data
