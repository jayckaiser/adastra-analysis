import os

import pandasql as psql

from utils.io_utils import get_config, load_data, load_yaml, save_tsv


def main():

    # Collect the filepaths to be passed around the script.
    queries_config_path = '../configs/queries.yml'
    data_dir = get_config('data_dir')
    queries_dir = get_config('queries_dir')

    # Read in the NLP dataframe, and filter to only read text.
    data = load_data(data_dir, nlp=True, is_read=False, drop_lists=True)

    # Load the analytics config and characters to use in analysis
    queries = load_yaml(queries_config_path)

    for file, query_params in queries.items():

        try:
            sql_query = query_params['sql']
            queried_df = psql.sqldf(sql_query)

            output_filepath = os.path.join(queries_dir, file + '.tsv')
            save_tsv(queried_df, output_filepath)

            print(f"Saved query output to '{output_filepath}'.")
        
        except Exception as err:
            print(f"! Query failed: \n{sql_query} \n{err}")


if __name__ == '__main__':
    main()
