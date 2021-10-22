import pandas as pd
import pandasql as psql

from utils.utils import prepare_directories


class Dataset(pd.DataFrame):
    """
    Extension of Pandas DataFrame.

    This contains several PandaSQL helpers and disk-output helpers.
    """
    def __init__(self, data, columns=None):
        # Create the DataFrame, depending on type of input.

        # Dataset or DataFrame is given.
        if isinstance(data, Dataset) or isinstance(data, pd.DataFrame):
            super().__init__(data=data)
        
        # Local filepath is given.
        elif isinstance(data, str):
            _data = pd.read_json(
                data,
                orient='records',
                lines=True
            )
            super().__init__(data=_data)
        
        # Dictionary and column names are given.
        else: 
            super().__init__(
                data=list(data.items()),
                columns=columns
            )

    def copy(self):
        """
        Extend copy to return a Dataset.
        """
        return Dataset(super().copy())


    def filter_where(self, filters):
        """
        Apply one or more where-clauses to the dataset, using the alias provided in the PandaSQL query.
        """
        _data = self.copy()

        if filters is not None:
            
            # Allow either a str or List[str].
            if isinstance(filters, str):
                filters = [filters]
            
            for where_clause in filters:

                _data = psql.sqldf(f"""
                    select * from _data
                    where {where_clause}
                """)

        return Dataset(_data)

    
    def add_columns(self, selects):
        """
        Logic to add additional columns to a dataset.
        """
        _data = self.copy()

        if selects is not None:
            formatted_selects = ',\n'.join(selects)
           
            _data = psql.sqldf(f"""
                select *,
                    {formatted_selects}
                from _data
            """)
        
        return Dataset(_data)


    @classmethod
    def query_psql(cls, datasets, sql_query):
        """
        Complete a full SQL query, using one or more provided datasets.

        (This is a wrapper to simplify executing PandaSQL queries.)
        """
        for dataset_name, _dataset in datasets.items():
            exec(f"{dataset_name} = _dataset")

        _data = psql.sqldf(sql_query)

        return Dataset(_data)



    # Functions to write the Dataset in different formats.
    def to_jsonl(self, filepath):
        """
        Write the dataset as JSON lines.
        """
        prepare_directories(filepath)
        self.to_json(filepath, orient='records', lines=True)
    

    def to_tsv(self, filepath):
        """
        Write the dataset as TSV.
        (Maybe this would be useful for displaying?)
        """
        prepare_directories(filepath)
        self.to_csv(filepath, sep='\t', index=False)


    def to_txt(self, filepath, column, sep='\n'):
        """
        Write a given column to a filepath as text.
        """
        prepare_directories(filepath)

        lines = self[column].tolist()

        with open(filepath, 'w') as fp:
            fp.write( sep.join(lines) )
        