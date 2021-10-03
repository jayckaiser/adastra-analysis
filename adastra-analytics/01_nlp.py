import os

from utils.io_utils import get_config, read_dataframe, save_dataframe
from utils.nlp_utils import nlp_transform_df


def main():
    data_dir = get_config('data_dir')
    cleaned_data_path = os.path.join(data_dir, 'adastra.json')
    df = read_dataframe(cleaned_data_path)

    # Filter to only lines that contain read dialogue/narration.
    df = df.query('is_read == True')

    # Complete the NLP transformations on the dataframe.
    nlp_df = nlp_transform_df(df)

    # Resave the result as a new file.
    output_filepath = os.path.join(data_dir, 'adastra_nlp.json')
    save_dataframe(nlp_df, output_filepath)

    print(f"Saved NLP-processed dataframe to '{output_filepath}'")

if __name__ == '__main__':
    main()
