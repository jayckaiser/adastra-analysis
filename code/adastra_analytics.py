import os
import sys

from utils.utils import merge_dicts

from configs import Configs
from dataset import Dataset
from relplot import Relplot
from wordcloud_image import WordcloudImage

from utils.adastra_dataset_utils import build_adastra_data
from utils.adastra_nlp_dataset_utils import nlp_augment_adastra_data
from utils.tfidf_utils import get_term_freqs, filter_term_freqs, build_filtered_tfidf_word_freqs
from utils.screenplay_utils import format_rows_to_lines


class AdastraAnalytics:
    CONFIGS_FILEPATH = '../configs.yml'

    def __init__(self, configs_filepath=CONFIGS_FILEPATH, build_dataset=False, use_nlp=False):
        self.yaml_configs = Configs.load_yaml(configs_filepath)
        
        # Verify necessary configs are present, then collect.
        dataset_configs = self.yaml_configs.get('dataset_configs')
        dataset_configs.check_keys(
            ['adastra_directory', 'adastra_datapath', 'main_character']
        )
        self.adastra_directory = dataset_configs.get('adastra_directory')
        adastra_datapath = dataset_configs.get('adastra_datapath')
        main_character   = dataset_configs.get('main_character')

        # Build the adastra dataset.
        self.adastra_dataset = self.get_adastra_dataset(
            self.adastra_directory, adastra_datapath,
            main_character=main_character,
            build_dataset=build_dataset, use_nlp=use_nlp
        )

        # Instantiate extra datasets.
        self.datasets = self.build_datasets()



    @staticmethod
    def get_adastra_dataset(
        adastra_directory: str, adastra_datapath: str,
        main_character: str,
        build_dataset: bool, use_nlp: bool
    ) -> Dataset:
        """

        """
        # Recreate the dataset if specified.
        if build_dataset is True:
            print(f"Building Adastra dataset using script files in `{adastra_directory}`...")
            adastra_data = build_adastra_data(adastra_directory, main_character=main_character)
            print("Dataset built!")

            # Apply optional NLP processing if specified.
            if use_nlp is True:
                print(
                    "Augmenting dataset with NLP... (This process takes about a minute.)"
                )
                adastra_data = nlp_augment_adastra_data(adastra_data)
                print("Dataset augmented!")

            # Save whichever version to disk.
            Dataset(adastra_data).to_jsonl(adastra_datapath)
            print(f"Dataset saved to `{adastra_datapath}`.")

        # Load in the saved Dataset from disk.
        if os.path.exists(adastra_datapath):
            adastra_dataset = Dataset(adastra_datapath)
            print(f"Successfully loaded Adastra dataset from `{adastra_datapath}`!")

            return adastra_dataset
        
        else:
            print(
                f"File not found at `{adastra_datapath}`\n"
                "Are you sure it has been created?\n"
                "If this is your first time running, please set `build_dataset` flag to `True`."
            )
            sys.exit(0)



    def build_datasets(self):
        """
        
        """
        print("\nBuilding extra datasets from `adastra_analytics.datasets`.")

        # 
        datasets_configs = self.yaml_configs.get('datasets')
        if datasets_configs is None:
            print("* No extra datasets found.")
            return {}

        # 
        datasets = {}

        for dataset_configs in datasets_configs:

            # Verify all required keys are present in each dataset.
            dataset_configs.check_keys(
                ['name', 'columns', 'data']
            )

            # 
            dataset = Dataset(
                dataset_configs.get('data'),
                columns=dataset_configs.get('columns')
            )

            # 
            name = dataset_configs.get('name')
            datasets[name] = dataset
            print(f"* `{name}` dataset built.")

        return datasets
    


    def run_queries(self):
        """
        
        """
        print("\nProcessing queries from `adastra_analytics.queries`.")

        # 
        global_configs = self.yaml_configs.get('adastra_analytics').get('queries')
        if global_configs is None:
            print("No queries found!")
            return

        # 
        global_configs.check_keys(
            ['output_directory', 'dataset_alias', 'queries']
        )

        # Filter the adastra dataset further if specified.
        _adastra_dataset = Dataset(self.adastra_dataset) \
            .filter_where(global_configs.get('where'))

        # Iterate and build each query.
        for query_configs in global_configs.get('queries'):

            # 
            query_configs.check_keys(
                ['name', 'sql']
            )

            # Filter the adastra dataset further if specified.
            # Add to the dictionary of datasets.
            datasets = self.datasets.copy()

            dataset_alias = global_configs.get('dataset_alias') 
            datasets[dataset_alias] = Dataset(_adastra_dataset) \
                .filter_where(query_configs.get('where'))

            # 
            output_dataset = Dataset.query_psql(
                datasets,
                sql_query=query_configs.get('sql')
            )

            # 
            output_directory = global_configs.get('output_directory')
            output_file      = query_configs.get('name')
            output_filepath  = os.path.join(output_directory, output_file)
            output_dataset.to_jsonl(output_filepath)

            print(f"* Query results saved to `{output_filepath}`.")



    def run_relplots(self):
        """
        
        """
        print("\nBuilding relplots from `adastra_analytics.relplots`.")

        # 
        global_configs = self.yaml_configs.get('adastra_analytics').get('relplots')
        if global_configs is None:
            print("* No relplots found!")
            return

        # 
        global_configs.check_keys(
            ['output_directory', 'dataset_alias', 'relplot_args', 'relplots']
        )
        
        # Filter the adastra dataset further if specified.
        _adastra_dataset = Dataset(self.adastra_dataset) \
            .filter_where(global_configs.get('where'))

        # Iterate and build each query.
        for relplot_configs in global_configs.get('relplots'):

            # 
            relplot_configs.check_keys(
                ['name', 'sql']
            )

            # Filter the adastra dataset further if specified.
            # Add to the dictionary of datasets.
            datasets = self.datasets.copy()

            dataset_alias = global_configs.get('dataset_alias')
            datasets[dataset_alias] = Dataset(_adastra_dataset) \
                .filter_where(relplot_configs.get('where'))

            # 
            output_dataset = Dataset.query_psql(
                datasets,
                sql_query=relplot_configs.get('sql')
            )

            # Combine the relplot args of each config with the global args.
            relplot_args = merge_dicts(
                global_configs.get('relplot_args'),
                relplot_configs.get('relplot_args')
            )

            output_relplot = Relplot(
                output_dataset,
                relplot_args=relplot_args,
                figsize=relplot_configs.get('figsize'),
                axhline=relplot_configs.get('axhline'),
                remove_outliers=relplot_configs.get('remove_outliers')
            )

            # 
            output_directory = global_configs.get('output_directory')
            output_file = relplot_configs.get('name')
            output_filepath = os.path.join(output_directory, output_file)
            output_relplot.to_disk(output_filepath)

            print(f"* Relplot saved to `{output_filepath}`.")

            

    def run_wordclouds(self):
        """
        
        """
        print("\nBuilding wordclouds from `adastra_analytics.wordclouds`.")

        # 
        global_configs = self.yaml_configs.get('adastra_analytics').get('wordclouds')
        if global_configs is None:
            print("* No wordclouds found!")
            return

        # 
        global_configs.check_keys(
            ['output_directory',
             'documents_column', 'filter_columns',
             'tfidf_args', 'wordcloud_args',
             'wordclouds']
        )
        
        # Filter the adastra dataset further if specified.
        _adastra_dataset = Dataset(self.adastra_dataset) \
            .filter_where(global_configs.get('where'))

        term_freqs = get_term_freqs(
            _adastra_dataset,
            index=global_configs.get('filter_columns'),
            doc_col=global_configs.get('documents_column'),
            tfidf_args=global_configs.get('tfidf_args'),
        )

        # Iterate and build each query.
        for wordcloud_configs in global_configs.get('wordclouds'):

            # 
            wordcloud_configs.check_keys(
                ['name', 'where']
            )

            # 
            image_filepath = wordcloud_configs.get(
                'image_filepath',
                os.path.join(
                    self.adastra_directory,
                    'game/images',
                    wordcloud_configs.get('name') 
                )
            )

            try:
                # 
                filtered_term_freqs = filter_term_freqs(
                    term_freqs,
                    filters=wordcloud_configs.get('where')
                )
                
                # 
                word_freqs = build_filtered_tfidf_word_freqs(
                    term_freqs, filtered_term_freqs
                )

                # 
                wordcloud_args = merge_dicts(
                    global_configs.get('wordcloud_args'),
                    wordcloud_configs.get('wordcloud_args')
                )

                wordcloud = WordcloudImage(
                    word_freqs,
                    image_filepath = image_filepath,
                    wordcloud_args = wordcloud_args
                )

                # 
                output_directory = global_configs.get('output_directory')
                output_file = wordcloud_configs.get('name')
                output_filepath = os.path.join(output_directory, output_file)
                wordcloud.to_disk(output_filepath)

                print(f"* Wordcloud saved to `{output_filepath}`.")

            
            except Exception as err:
                print(f"!!! Failed to build wordcloud for `{image_filepath}` :: {err}")
            

    def run_screenplays(self):
        """
        
        """
        print("\nProcessing screenplays from `adastra_analytics.screenplays`.")

        # 
        global_configs = self.yaml_configs.get('adastra_analytics').get('screenplays')
        if global_configs is None:
            print("No screenplays found!")
            return

        # 
        global_configs.check_keys(
            ['output_directory', 'screenplays',]
        )

        # Filter the adastra dataset further if specified.
        _adastra_dataset = Dataset(self.adastra_dataset) \
            .filter_where(global_configs.get('where'))

        # Iterate and build each query.
        for screenplay_configs in global_configs.get('screenplays'):

            # 
            screenplay_configs.check_keys(
                ['name', 'formats',]
            )
            output_type = screenplay_configs.get('name')
            justify     = screenplay_configs.get('justify')
            line_sep    = screenplay_configs.get('line_sep', '\n')
            formats     = screenplay_configs.get('formats')

            # Filter the adastra dataset further if specified.
            # Add new columns if specified.
            screenplay_dataset = (
                _adastra_dataset
                    .filter_where(screenplay_configs.get('where'))
                    .add_columns(screenplay_configs.get('add_columns'))
            )

            # Transform the dataset's lines into formatted lines.
            formatted_screenplay_dataset = format_rows_to_lines(
                screenplay_dataset,
                formats=formats,
                justify=justify,
            )

            # Iterate the file names and output each as a separate file.
            for file in formatted_screenplay_dataset['file'].unique():
                formatted_screenplay_subset = formatted_screenplay_dataset \
                    .filter_where(f'file = "{file}"')

                # 
                output_folderpath = os.path.join(
                    global_configs.get('output_directory'),
                    output_type
                )
                output_filepath = os.path.join(output_folderpath, file + '.txt')
                
                formatted_screenplay_subset.to_txt(output_filepath, 'line', sep=line_sep)

            print(f"* Saved all screenplays for {output_type} to `{output_folderpath}`.")
