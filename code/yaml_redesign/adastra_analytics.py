import os
import sys

from utils.utils import merge_dicts

from classes.configs import Configs
from classes.dataset import Dataset
from classes.query import Query

from utils.tfidf_utils import get_term_freqs

from adastra_dataset import build_adastra_data
from adastra_nlp_dataset import nlp_augment_adastra_data
from adastra_analytics_mains import query_main, relplot_main, screenplay_main, wordcloud_main


class AdastraAnalytics:
    

    def __init__(self, configs_filepath):
        
        self.yaml_configs = Configs.load_configs(configs_filepath)
        self.dataset_configs = self.yaml_configs.get('datasets').get('datasets')


        self.datasets = {}



    def build_datasets(self):
        """
        
        """
        print("\nBuilding datasets for run...")

        for dataset_config in self.dataset_configs:
            name = dataset_config['name']

            if AdastraDataset():
                _dataset = AdastraDataset(**dataset_config)
            
            elif Dataset():
                _dataset = Dataset(**dataset_config)

            elif TermFrequencies():
                _dataset = TermFrequencies(**dataset_config)
            
            else:
                print(f"! Dataset `{name}` is an undefined dataset object!")
                sys.exit(0)

            self.datasets[name] = _dataset



    def load_datasets(self):
        """
        
        """
        print("\nLoading datasets for run...")

        for dataset_config in self.dataset_configs:
            name = dataset_config['name']
            file = dataset_config['file']

            try:
                _dataset = Dataset.load_dataset(file)
                self.datasets[name] = _dataset
                print(f"* Dataset `{name}` loaded: `{file}`")

            except Exception as err:
                print(
                    f"! Dataset `{name}` not found at `{file}`\n"
                    "! Are you sure it has been created?\n"
                    "! If this is your first time running, please use `--datasets`."
                )
                print(err)
                sys.exit(0)



    def build_adastra_dataset(self, use_nlp=False) -> Dataset:
        """

        """
        print(f"\nBuilding Adastra dataset using script files in `{self.adastra_directory}`...")
        adastra_data = build_adastra_data(self.adastra_directory, main_character=self.main_character)

        # Apply optional NLP processing if specified.
        if use_nlp is True:
            print(
                "@ Augmenting dataset with NLP... (This process takes about a minute.)"
            )
            adastra_data = nlp_augment_adastra_data(adastra_data)
            print("@ Dataset augmented!")

        self.adastra_dataset = Dataset(adastra_data)
    


    def run_queries(self, queries=None):
        """
        
        """
        print("\nProcessing queries...")

        # Retrieve the queries configs to process from the Configs.
        query_configs = self.yaml_configs.get('queries').get('queries')
        if query_configs is None:
            print("No queries found!")
            return
    

         # Iterate and build each query.
        for query_config in query_configs:
            name = query_config.get('name')

            # Process selected queries if specified. Otherwise, run all.
            if queries and name not in queries:
                continue

            Query(**query_config)




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
            defined_relplots.check_keys(relplots, exit=False)

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
            _title           = relplot_configs.get('title')
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
                title=_title,
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
            defined_screenplays.check_keys(screenplays, exit=False)

        # Iterate and build each screenplay.
        for screenplay_name, screenplay_configs in defined_screenplays.items():

            # Process selected screenplays if specified. Otherwise, run all.
            if screenplays and screenplay_name not in screenplays:
                continue

            # Verify required arguments are defined, then retrieve all.
            screenplay_configs.check_keys(
                ['folder', 'categories',]
            )
            folder       = screenplay_configs.get('folder')
            categories   = screenplay_configs.get('categories')
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

                categories=categories,
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
            defined_wordclouds.check_keys(wordclouds, exit=False)

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
            _image = wordcloud_configs.get('image_file')
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
