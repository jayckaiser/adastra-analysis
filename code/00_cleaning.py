import os

from utils.raw_utils import script_filepaths_to_df
from utils.clean_utils import full_clean_transform_df
from utils.io_utils import get_config, save_dataframe


def main():
    script_files = [
        'a1s1', 'a1s2', 'a1s3', 'a1s4', 'a1s5', 'a1s6', 'a1s7',
        'a2s1', 'a2s2', 'a2s3',
        'a3s1', 'a3s2',
        'end_game1', 'end_game2',
    ]

    # The raw data dir is defined in the paths config.
    adastra_dir = get_config('adastra_dir')

    # Convert script filenames into full paths.
    script_filepaths = [
        os.path.join(adastra_dir, 'game', script_file + '.rpy')
        for script_file in script_files
    ]

    # Load all rows into a simple dataframe.
    raw_df = script_filepaths_to_df(script_filepaths)

    # Transform the dataframe with additional metadata and cleaning.
    cleaned_df = full_clean_transform_df(raw_df)

    # Save the dataframe to the cleaned data directory.
    data_dir = get_config('data_dir')

    output_filepath = os.path.join(data_dir, 'adastra.json')
    save_dataframe(cleaned_df, output_filepath)

    print(f"Saved contents of 14 game files to '{output_filepath}'")



if __name__ == '__main__':
    main()
