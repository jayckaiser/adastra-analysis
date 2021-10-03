import gc
import os

from utils.io_utils import get_config, get_wordcloud_list, read_dataframe, save_wordcloud 
from utils.nlp_utils import lines_to_tfs, get_queried_tf_word_frequencies
from utils.wordcloud_utils import make_wordcloud_image


def main():

    # Collect the filepaths to be passed around the script.
    data_dir = get_config('data_dir')
    adastra_dir = get_config('adastra_dir')
    images_dir = os.path.join(adastra_dir, 'game', 'images')
    wordclouds_dir = get_config('wordclouds_dir')

    # Read in the NLP dataframe, and filter to only read text.
    cleaned_data_path = os.path.join(data_dir, 'adastra_nlp.json')
    df = read_dataframe(cleaned_data_path)
    df = df.query('is_read == True')

    # Extract the Term Frequencies, then filter and normalize.
    # Note: I'm using non-stop words here; use `doc_col='line'` to use the cleaned text.
    tf = lines_to_tfs(
        df, doc_col='content_words',
        max_df=0.3, min_df=5, 
    )
    print(f"Completed TF calculations!")


    # Read in the YAML list of wordclouds to make.
    wordcloud_list = get_wordcloud_list()

    # Iterate the wordcloud params.
    # Create wordclouds based on an input filename and TF filter statements.
    for wordcloud_params in wordcloud_list:

        images_subdir = wordcloud_params['subfolder']
        filter_query  = wordcloud_params['query']
        images_to_do  = wordcloud_params['images']

        # Note: a query can be applied here to specify a specific character, file, or scene.
        word_frequencies = get_queried_tf_word_frequencies(tf, filter_query)
        print(f'Filtered TFs by "{filter_query}"')

        for image_file in images_to_do:

            try:
                image_path = os.path.join(images_dir, images_subdir, image_file)
                
                # Create the actual wordcloud.
                # Note: All kwargs go into wordcloud.WordCloud init.
                # (P.S. I'm not beholden to any of these parameters.)
                wc = make_wordcloud_image(
                    word_frequencies, image_path,
                    max_words=2000, max_font_size=40,
                    background_color="black",              # Toggle these for a transparent background.
                    # mode="RGBA", background_color=None,  # Toggle these for a transparent background.
                    repeat=True, relative_scaling=0.5,
                    random_state=42,
                )

                # Save the wordcloud to disk, and delete the object to save memory.
                output_path = os.path.join(wordclouds_dir, images_subdir, image_file)
                save_wordcloud(wc, output_path)

                print(f"Saved wordcloud for {image_file}")
                del wc

            except FileNotFoundError:
                print(f"!!! File not found: `{image_path}`")

        del word_frequencies



if __name__ == '__main__':
    main()
