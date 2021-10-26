import pandas as pd
import pandasql as psql

from utils.utils import prepare_directories


class Dataset:
    """
    Extension of pandas DataFrame for interfacing with SQL commands.
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
        self.data = self.build_dataset(data, columns=columns)

        self.data = self.filter_where(where)
        self.data = self.query_sql(sql, dataset_alias, datasets)


    @staticmethod
    def build_dataset(data, columns=None):
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

        return _data


    def query_sql(self, sql_query, alias, datasets=None):
        """
        
        """
        _data = self.data.copy()

        if sql_query and alias:
            exec(f"{alias} = _data")

        if datasets:
            for dataset_name, dataset in datasets.items():
                exec(f"{dataset_name} = dataset.copy()")

        _data = psql.sqldf(sql_query)

        return _data


    def get_data(self):
        """
        Exit the Dataset.
        """
        return self.data
