import os
import pandas as pd
import sys

from utils.io_utils import get_config, load_data

pd.set_option('display.max_rows'    , None)
pd.set_option('display.max_columns' , None)
pd.set_option('display.width'       , None)
pd.set_option('display.max_colwidth', None)


def main():

    try:
        query = sys.argv[1].lower()
    except:
        print("No query provided! Add a collocation as an argument!")

    # Read in the cleaned dataframe, and filter to only read text.
    data_dir = get_config('data_dir')
    df = load_data(data_dir, nlp=False, is_read=False)
    
    # Filter the dataframe to non-renpy lines (this keeps `is_choice == True` rows).
    df = df.query('is_renpy == False')

    found_rows = df[(
        df['line']
            .str.lower()
            .str.contains(query)
    )]

    print(found_rows[
        ['file', 'line_idx', 'speaker', 'is_choice', 'is_optional', 'line']
    ])


if __name__ == '__main__':
    main()
