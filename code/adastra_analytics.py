import os
import sys

from utils.utils import merge_dicts

from classes.configs import Configs
from classes.dataset import Dataset

from utils.tfidf_utils import get_term_freqs

from adastra_dataset import build_adastra_data
from adastra_nlp_dataset import nlp_augment_adastra_data
from adastra_analytics_mains import query_main, relplot_main, screenplay_main, wordcloud_main


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

        for dataset_name, dataset_configs in datasets_configs.items():

            # Verify all required keys are present, then build the dataset.
            dataset_configs.check_keys(
                ['columns', 'data']
            )
            columns = dataset_configs.get('columns') 
            data    = dataset_configs.get('data') 

            dataset = Dataset(data, columns=columns)

            # 
            datasets[dataset_name] = dataset
            print(f"* `{dataset_name}` dataset built.")

        return datasets
    


    def run_queries(self, queries=None):
        """
        
        """
        print("\nProcessing queries from `adastra_analytics.queries`.")

        # Retrieve the queries configs to process from the Configs.
        global_configs = self.yaml_configs.get('adastra_analytics').get('queries')
        if global_configs is None:
            print("No queries found!")
            return

        # Verify required arguments are defined, then retrieve all.
        global_configs.check_keys(
            ['output_directory', 'dataset_alias', 'queries']
        )
        output_directory = global_configs.get('output_directory')
        dataset_alias    = global_configs.get('dataset_alias')
        defined_queries  = global_configs.get('queries')
        _global_where    = global_configs.get('where')
        

        # Filter the adastra dataset further if specified.
        _adastra_dataset = Dataset(self.adastra_dataset) \
            .filter_where(_global_where)

        # Verify selected queries are present, if provided.
        if queries:
            defined_queries.check_keys(queries)

        # Iterate and build each query.
        for query_name, query_configs in defined_queries.items():
            
            # Process selected queries if specified. Otherwise, run all.
            if queries and query_name not in queries:
                continue

            # Verify required arguments are defined, then retrieve all.
            query_configs.check_keys(
                ['file', 'sql']
            )
            file  = query_configs.get('file')
            sql   = query_configs.get('sql')
            _where = query_configs.get('where')

            output_filepath = os.path.join(output_directory, file)

            query_main(
                query_name,

                adastra_dataset=_adastra_dataset,
                dataset_alias=dataset_alias,
                where=_where,
                datasets=self.datasets,
                sql=sql,

                output_file=output_filepath,
            )



    def run_relplots(self, relplots=None):
        """
        
        """
        print("\nBuilding relplots from `adastra_analytics.relplots`.")

        #  Retrieve the relplots configs to process from the Configs.
        global_configs = self.yaml_configs.get('adastra_analytics').get('relplots')
        if global_configs is None:
            print("* No relplots found!")
            return

        # Verify required arguments are defined, then retrieve all.
        global_configs.check_keys(
            ['output_directory', 'dataset_alias', 'relplot_args', 'relplots']
        )
        output_directory    = global_configs.get('output_directory')
        dataset_alias       = global_configs.get('dataset_alias')
        global_relplot_args = global_configs.get('relplot_args')
        defined_relplots    = global_configs.get('relplots')
        _global_where       = global_configs.get('where')
        
        # Filter the adastra dataset further if specified.
        _adastra_dataset = Dataset(self.adastra_dataset) \
            .filter_where(_global_where)

        # Verify selected relplots are present, if provided.
        if relplots:
            defined_relplots.check_keys(relplots)

        # Iterate and build each relplot.
        for relplot_name, relplot_configs in defined_relplots.items():

            # Process selected relplots if specified. Otherwise, run all.
            if relplots and relplot_name not in relplots:
                continue
            
            # Verify required arguments are defined, then retrieve all.
            relplot_configs.check_keys(
                ['file', 'sql']
            )
            file             = relplot_configs.get('file')
            sql              = relplot_configs.get('sql')
            _where           = relplot_configs.get('where')
            _relplot_args    = relplot_configs.get('relplot_args')
            _figsize         = relplot_configs.get('figsize')
            _axhline         = relplot_configs.get('axhline')
            _remove_outliers = relplot_configs.get('remove_outliers')

            # Combine the relplot args of each config with the global args.
            relplot_args = merge_dicts(
                global_relplot_args,
                _relplot_args
            )

            output_filepath = os.path.join(output_directory, file)

            relplot_main(
                relplot_name,

                adastra_dataset=_adastra_dataset,
                dataset_alias=dataset_alias,
                where=_where,
                datasets=self.datasets,
                sql=sql,

                relplot_args=relplot_args,
                figsize=_figsize,
                axhline=_axhline,
                remove_outliers=_remove_outliers,

                output_file=output_filepath,
            )


    
    def run_screenplays(self, screenplays=None):
        """
        
        """
        print("\nProcessing screenplays from `adastra_analytics.screenplays`.")

        # Retrieve the relplots configs to process from the Configs.
        global_configs = self.yaml_configs.get('adastra_analytics').get('screenplays')
        if global_configs is None:
            print("No screenplays found!")
            return

        # Verify required arguments are defined, then retrieve all.
        global_configs.check_keys(
            ['output_directory', 'screenplays']
        )
        output_directory    = global_configs.get('output_directory')
        defined_screenplays = global_configs.get('screenplays')
        _global_where       = global_configs.get('where')

        # Filter the adastra dataset further if specified.
        _adastra_dataset = Dataset(self.adastra_dataset) \
            .filter_where(_global_where)

        # Verify selected queries are present, if provided.
        if screenplays:
            defined_screenplays.check_keys(screenplays)

        # Iterate and build each screenplay.
        for screenplay_name, screenplay_configs in defined_screenplays.items():

            # Process selected screenplays if specified. Otherwise, run all.
            if screenplays and screenplay_name not in screenplays:
                continue

            # Verify required arguments are defined, then retrieve all.
            screenplay_configs.check_keys(
                ['folder', 'formats',]
            )
            folder       = screenplay_configs.get('folder')
            formats      = screenplay_configs.get('formats')
            _where       = screenplay_configs.get('where')
            _add_columns = screenplay_configs.get('add_columns')
            _justify     = screenplay_configs.get('justify')
            _line_sep    = screenplay_configs.get('line_sep', '\n')

            output_folderpath = os.path.join(output_directory, folder)

            screenplay_main(
                screenplay_name,

                adastra_dataset=_adastra_dataset,
                where=_where,
                add_columns=_add_columns,

                formats=formats,
                justify=_justify,
                line_sep=_line_sep,

                output_folder=output_folderpath
            )

            

    def run_wordclouds(self, wordclouds=None):
        """
        
        """
        print("\nBuilding wordclouds from `adastra_analytics.wordclouds`.")

        # Retrieve the relplots configs to process from the Configs.
        global_configs = self.yaml_configs.get('adastra_analytics').get('wordclouds')
        if global_configs is None:
            print("* No wordclouds found!")
            return

        # Verify required arguments are defined, then retrieve all.
        global_configs.check_keys(
            ['output_directory',
             'documents_column', 'filter_columns',
             'tfidf_args', 'wordcloud_args',
             'wordclouds']
        )
        output_directory      = global_configs.get('output_directory')
        documents_column      = global_configs.get('documents_column')
        filter_columns        = global_configs.get('filter_columns')
        tfidf_args            = global_configs.get('tfidf_args')
        global_wordcloud_args = global_configs.get('wordcloud_args')
        defined_wordclouds    = global_configs.get('wordclouds')
        _global_where         = global_configs.get('where')
        
        # Filter the adastra dataset further if specified.
        _adastra_dataset = Dataset(self.adastra_dataset) \
            .filter_where(_global_where)

        # Build the term freqs for the entire dataset (to be filtered later).
        term_freqs = get_term_freqs(
            _adastra_dataset,
            index=filter_columns,
            doc_col=documents_column,
            tfidf_args=tfidf_args,
        )

        # Verify selected wordclouds are present, if provided.
        if wordclouds:
            defined_wordclouds.check_keys(wordclouds)

        for wordcloud_name, wordcloud_configs in defined_wordclouds.items():

            # Process selected wordclouds if specified. Otherwise, run all.
            if wordclouds and wordcloud_name not in wordclouds:
                continue
            
            # Verify required arguments are defined, then retrieve all.
            wordcloud_configs.check_keys(
                ['file', 'where']
            )
            file   = wordcloud_configs.get('file')
            where  = wordcloud_configs.get('where')
            _image = wordcloud_configs.get('image_filepath')
            _wordcloud_args = wordcloud_configs.get('wordcloud_args')

            # Both global and specific args are provided.
            # Build the wordcloud with these based on the image.
            wordcloud_args = merge_dicts(
                global_wordcloud_args,
                _wordcloud_args
            )

            # The image_filepath can be optionally specified.
            # Otherwise, assume it is sourced from the game files.
            game_filepath = os.path.join(
                self.adastra_directory, 'game/images', file
            )
            image_filepath = _image or game_filepath

            output_filepath = os.path.join(output_directory, file)

            wordcloud_main(
                wordcloud_name,

                term_freqs=term_freqs,
                where=where,

                image_file=image_filepath,
                wordcloud_args=wordcloud_args,
                
                output_file=output_filepath,
            )
