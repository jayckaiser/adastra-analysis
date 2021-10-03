import os
import pandas as pd
import sys

from utils.io_utils import get_config, read_dataframe

pd.set_option('display.max_rows'    , None)
pd.set_option('display.max_columns' , None)
pd.set_option('display.width'       , None)
pd.set_option('display.max_colwidth', None)


def main():

    try:
        file = sys.argv[1].replace('.rpy', '').lower()
    except:
        print("No file specified! Add a filename as an argument!")

    # Read in the NLP dataframe, and filter to only read text.
    data_dir = get_config('data_dir')
    cleaned_data_path = os.path.join(data_dir, 'adastra.json')
    df = read_dataframe(cleaned_data_path)
    df = df.query('is_read == True')

    file_df = df.query(f"file == '{file.lower()}'")
    print(
        file_df[
            ['line_idx', 'speaker', 'is_optional', 'line']
        ]
    )


if __name__ == '__main__':
    main()
