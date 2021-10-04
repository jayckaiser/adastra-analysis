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
        filter_query = sys.argv[1]
    except:
        print("No filter query specified! Add a filter as an argument!")
        return

     # Read in the cleaned dataframe, and filter to only read text.
    data_dir = get_config('data_dir')
    df = load_data(data_dir, nlp=False, is_read=False)

    print(
        df.query(filter_query)
    )


if __name__ == '__main__':
    main()
