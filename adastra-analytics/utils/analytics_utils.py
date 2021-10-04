import numpy as np
import pandas as pd
from scipy import stats

import pandasql as psql


def build_grouped_graph_data(data, agg, alias, proportion=False):
    """
    Standardized method to apply an aggregate by character and file.
    """
    # Standardize the data name to pass to pSQL.
    passed_dataframe = data

    # There is different logic for a proportional aggregate.
    if proportion:
        file_counts = psql.sqldf(f"""
            select
                file,
                cast({agg} as float) as {alias}_by_file
            from passed_dataframe
            group by 1
            order by 1
        """)

        grouped = psql.sqldf(f"""
            select
                file,
                speaker,
                {agg} / {alias}_by_file as {alias}
            from passed_dataframe
                inner join file_counts using(file)
            group by 1, 2
            order by 1, 2
        """)

    else:
        grouped = psql.sqldf(f"""
            select
                file,
                speaker,
                {agg} as {alias}
            from passed_dataframe
            group by 1, 2
            order by 1, 2
        """)

    return grouped


def build_sentiment_graph_data(data, file=None, window_lines=9, col_name='rolling_sentiment'):
    """
    Standardized method to aggregate sentiment by file.
    """
    # Standardize the data name to pass to pSQL.
    passed_dataframe = data

    # Add a file filter if provided.
    if file == 'all' or not file:
        where_clause = ""
    else:
        where_clause = f"where file = '{file}'"

    # Run the sentiment query on the data.
    df = psql.sqldf(f"""
        select
            file,
            line_idx,
            speaker,
            avg(sentiment) over (
                partition by file, speaker
                order by line_idx
                rows between {window_lines} preceding and current row
            ) as {col_name}

        from passed_dataframe

        {where_clause}
    """)
    
    # Remove huge outliers typical at beginning and end of window.
    df = df[
        (np.abs(stats.zscore(df['rolling_sentiment'])) < 3)
    ]

    return df
