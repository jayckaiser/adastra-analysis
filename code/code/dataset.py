import pandas as pd
import pandasql as psql


class Dataset:
    """
    
    """
    def __init__(
        self,
        filepath=None,
        data=None, columns=None,
        filters=None,
    ):
        # Either create the dataset or load it from disk.
        if filepath is None:
            self.data = pd.DataFrame(
                list(data.to_dict()),
                columns=columns
            )
        else:
            self.data = pd.read_json(
                filepath,
                orient='records',
                lines=True
            )

        # Apply optional where-clauses to the dataset using PandaSQL.
        self.data = self.filter_where(filters)


    def filter_where(self, filters):
        """
        Apply one or more where-clauses to the dataset, using the alias provided in the PandaSQL query.
        """
        __data = self.data.copy()

        if filters is not None:
            
            # Allow either a str or List[str].
            if isinstance(filters, str):
                filters = [filters]
            
            for where_clause in filters:

                __data = psql.sqldf(f"""
                    select * from __data
                    where {where_clause}
                """)

        return __data
        

    # Functions to write the Dataset in different formats.
    def to_jsonl(self, filepath):
        """
        Write the dataset as JSON lines.
        """
        self.data.to_json(filepath, orient='records', lines=True)
    

    def to_tsv(self, filepath):
        """
        Write the dataset as TSV.
        (Maybe this would be useful for displaying?)
        """
        self.data.to_csv(filepath, sep='\t', index=False)

