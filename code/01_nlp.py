import os

from utils.io_utils import get_config, load_data, save_dataframe
from utils.nlp_utils import nlp_transform_df


def main():
    # Load the cleaned dataframe, filtering to only read text.
    data_dir = get_config('data_dir')
    df = load_data(data_dir, nlp=False, is_read=True)

    # Complete the NLP transformations on the dataframe.
    nlp_df = nlp_transform_df(df)

    # Resave the result as a new file.
    output_filepath = os.path.join(data_dir, 'adastra_nlp.json')
    save_dataframe(nlp_df, output_filepath)

    print(f"Saved NLP-processed dataframe to '{output_filepath}'")



if __name__ == '__main__':
    main()
