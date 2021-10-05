import os
import pandasql as psql

from utils.io_utils import get_config, load_data, load_yaml, save_figure
from utils.analytics_utils import build_dataset, build_figure

def main():

    # Collect the filepaths to be passed around the script.
    analytics_config_path = '../configs/analytics.yml'
    data_dir = get_config('data_dir')
    analytics_dir = get_config('analytics_dir')

    # Load both cleaned dataframes, removing list columns that fail in PandaSQL.
    adastra = load_data(data_dir, drop_lists=True)
    adastra_nlp = load_data(data_dir, nlp=True, drop_lists=True)


    # Load the analytics configs as predefined in `analytics.yml`.
    analytics_config = load_yaml(analytics_config_path)

    datasets = analytics_config.get('datasets')
    graphs   = analytics_config.get('graphs')


    # Build custom datasets to use for analytics (default is characters to filter on).
    if datasets is not None:
        for dataset_name, dataset_params in datasets.items():
            df = build_dataset(dataset_params)
            exec(f"{dataset_name} = df")


    # Build each graph and save as a Seaborn plot to the file specified.
    if graphs is not None:
        for filename, graph_params in graphs.items():

            sql_query = graph_params['sql']
            graph_kwargs = graph_params['kwargs']

            # These are optional meta-params that influence the final plot.
            figsize = graph_params.get('figsize')
            axhline = graph_params.get('axhline')
            remove_outliers = graph_params.get('remove_outliers', False)

            # Run the filter query on the data, then create the figure.
            data = psql.sqldf(sql_query)
            fig  = build_figure(
                data,
                figsize=figsize,
                axhline=axhline,
                remove_outliers=remove_outliers,
                **graph_kwargs
            )

            # Save the figure to the specified filepath.
            filepath = os.path.join(analytics_dir, filename + '.png')
            save_figure(fig, filepath)

            print(f"Aggregate graph written to '{filepath}'.")



if __name__ == '__main__':
    main()
