import os
import sys

from utils.screenplay_utils import dataframe_to_script_lines
from utils.io_utils import get_config, load_data, save_lines

def main():
    # Retrieve the optional version argument.
    try:
        version = int(sys.argv[1])
    except:
        print("No version specified! Defaulting to version 3!")
        version = 3

    # Load the cleaned dataframe.
    data_dir = get_config('data_dir')
    df = load_data(data_dir, nlp=False, is_read=False)

    # Narrow the data to non-renpy text.
    df = df.query('is_renpy == False')

    # Iterate each file and write the contents as a screenplay.
    distinct_files = sorted(df['file'].unique().tolist())
    for file in distinct_files:

        # Narrow the dataframe to the file of the specific data.
        file_df = df[df['file'] == file]

        # Read the contents as scripted lines.
        script_lines = dataframe_to_script_lines(file_df, version)
        script_lines = map(lambda x: x + '\n', script_lines)  # Add another whitespace to improve readability.

        screenplays_dir = get_config('screenplays_dir')
        output_filepath = os.path.join(screenplays_dir, file + '.txt')
        save_lines(script_lines, output_filepath)

        print(f"Wrote contents of '{file}' to '{output_filepath}' as a screenplay")
    

if __name__ == '__main__':
    main()