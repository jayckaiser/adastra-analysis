import os

from pandas.core.construction import array

from utils.io_utils import get_config, load_data, load_yaml, save_plot
from utils.analytics_utils import build_sentiment_graph_data, build_grouped_graph_data


def main():

    # Collect the filepaths to be passed around the script.
    analytics_config_path = '../configs/analytics.yml'
    data_dir = get_config('data_dir')
    analytics_dir = get_config('analytics_dir')

    # Load the cleaned NLP dataframe, filtering to only read text.
    df = load_data(data_dir, nlp=True, is_read=True)


    # Load the analytics config and characters to use in analysis
    analytics_config = load_yaml(analytics_config_path)

    characters = analytics_config['characters']
    characters_df = df[
        df['speaker'].isin(characters.keys())
    ]

    # Note! pSQL does not support ListTypes. Manually remove these columns!
    characters_df = characters_df \
        .drop(['sentences', 'words', 'content_words'], axis=1)


    print(f"Data collected and filtered to {len(characters)} characters.")

    # Load in the graphs to create. Exit if none are found.
    graphs = analytics_config.get('graphs')
    if not graphs:
        print(f"No graphs found in `{analytics_config_path}`")
        return

    # Iterate the sentiment graphs and save each as a file.
    if 'sentiment' in graphs:
        for file in graphs['sentiment']:

            sentiment_graph_data = build_sentiment_graph_data(
                characters_df,
                file=file,
            )

            # Define the output filepath.
            filepath = os.path.join(analytics_dir, 'sentiment', file + '.png')

            save_plot(
                sentiment_graph_data,
                filepath,
                x='line_idx', y='rolling_sentiment',
                hue='speaker',
                kind='line',
                palette=characters,
                axhline=0.0, 
            )

            print(f"Sentiment graph written to '{filepath}'.")

    # Iterate the aggregate graphs and save each as a file.
    if 'aggregates' in graphs:
        for file, agg_params in graphs['aggregates'].items():
            
            agg   = agg_params['agg']
            alias = agg_params['alias']
            proportion = agg_params.get('proportion', False)
            axhline = agg_params.get('axhline')

            aggregate_graph_data = build_grouped_graph_data(
                characters_df,
                agg=agg,
                alias=alias,
                proportion=proportion,
            )

            # Define the output filepath.
            filepath = os.path.join(analytics_dir, 'aggregates', file + '.png')

            save_plot(
                aggregate_graph_data,
                filepath,
                x='file', y=alias,
                hue='speaker',
                kind='line',
                palette=characters,
                axhline=axhline,
            )

            print(f"Aggregate graph written to '{filepath}'.")


if __name__ == '__main__':
    main()
