import os

from utils.screenplay_utils import dataframe_to_script_lines, row_to_script_lines_v3
from utils.io_utils import get_config, read_dataframe, save_lines

def main():

    data_dir = get_config('data_dir')   
    cleaned_data_path = os.path.join(data_dir, 'adastra.json')
    df = read_dataframe(cleaned_data_path)

    # Narrow the data to non-renpy text.
    df = df.query('is_renpy == False')

    # Iterate each file and write the contents as a screenplay.
    distinct_files = sorted(df['file'].unique().tolist())
    for file in distinct_files:

        # Narrow the dataframe to the file of the specific data.
        file_df = df[df['file'] == file]

        # Read the contents as scripted lines.
        script_lines = dataframe_to_script_lines(file_df, row_to_script_lines_v3)
        script_lines = map(lambda x: x + '\n', script_lines)  # Add another whitespace to improve readability.

        screenplays_dir = get_config('screenplays_dir')
        output_filepath = os.path.join(screenplays_dir, file + '.txt')
        save_lines(script_lines, output_filepath)

        print(f"Wrote contents of '{file}' to '{output_filepath}' as a screenplay")
    

if __name__ == '__main__':
    main()
