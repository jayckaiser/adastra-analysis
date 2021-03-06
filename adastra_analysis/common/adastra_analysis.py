import sys

from adastra_analysis.common.dataset import Dataset
from adastra_analysis.common.util import yaml_utils


class AdastraAnalysis:
    

    def __init__(self, configs_filepath):
        
        self.yaml_configs = yaml_utils.load_yaml(configs_filepath)

        self.dataset_configs    = self.yaml_configs.get('datasets'   , {}).get('datasets')
        self.query_configs      = self.yaml_configs.get('queries'    , {}).get('queries')
        self.relplot_configs    = self.yaml_configs.get('relplots'   , {}).get('relplots')
        self.screenplay_configs = self.yaml_configs.get('screenplays', {}).get('screenplays')
        self.wordcloud_configs  = self.yaml_configs.get('wordclouds' , {}).get('wordclouds')

        self.datasets = {}



    def build_datasets(self, datasets):
        """
        
        """
        print("\nBuilding datasets for run...")

        # Retrieve the queries configs to process from the Configs.
        if self.dataset_configs is None:
            print("@ No datasets found!")
            return

        # Iterate and build each query.
        for config in self.dataset_configs:
            name = config.name
            file = config.file

            # Process selected queries if specified. Otherwise, run all.
            if datasets and name not in datasets:

                # Still load the dataset so it can be used in other datasets.
                _dataset = Dataset.load_dataset(file)

            else:
                _dataset = config.build_dataset(self.datasets)
                Dataset.save(_dataset, file, info=True)

            self.datasets[name] = _dataset



    def load_datasets(self):
        """
        
        """
        print("\nLoading datasets for run...")

        for config in self.dataset_configs:

            try:
                name = config.name
                file = config.file

                _dataset = config.load_dataset(file)
                self.datasets[name] = _dataset
                print(f"* Dataset `{name}` loaded: `{file}`")

            except Exception as err:
                print(
                    f"! Dataset `{name}` not found at `{file}`\n"
                    "! Are you sure it has been created?\n"
                    "! If this is your first time running, please use `build`."
                )
                print(err)
                sys.exit(0)



    def run_queries(self, queries=None):
        """
        
        """
        print("\nProcessing queries...")

        # Retrieve the queries configs to process from the Configs.
        if self.query_configs is None:
            print("@ No queries found!")
            return
    
        # Iterate and build each query.
        for query in self.query_configs:

            # Process selected queries if specified. Otherwise, run all.
            if queries and query.name not in queries:
                continue

            try:
                query.run(self.datasets)
                print(f"* Query `{query.name}` completed: {query.file}")

            except Exception as err:
                print(f"! Query `{query.name}` failed build: {err}")            



    def run_relplots(self, relplots=None):
        """
        
        """
        print("\nProcessing relplots...")

        # Retrieve the queries configs to process from the Configs.
        if self.query_configs is None:
            print("@ No relplots found!")
            return
    
        # Iterate and build each query.
        for relplot in self.relplot_configs:

            # Process selected queries if specified. Otherwise, run all.
            if relplots and relplot.name not in relplots:
                continue

            try:
                relplot.run(self.datasets)
                print(f"* Relplot `{relplot.name}` completed: {relplot.file}")

            except Exception as err:
                print(f"! Relplot `{relplot.name}` failed build: {err}")
            


    def run_screenplays(self, screenplays=None):
        """
        
        """
        print("\nProcessing screenplays...")

        # Retrieve the queries configs to process from the Configs.
        if self.screenplay_configs is None:
            print("@ No screenplays found!")
            return
    
        # Iterate and build each query.
        for screenplay in self.screenplay_configs:

            # Process selected queries if specified. Otherwise, run all.
            if screenplays and screenplay.name not in screenplays:
                continue

            try:
                screenplay.run(self.datasets)
                print(f"* Screenplay `{screenplay.name}` completed: {screenplay.folder}")

            except Exception as err:
                print(f"! Screenplay `{screenplay.name}` failed build: {err}")


    
    def run_wordclouds(self, wordclouds=None):
        """
        
        """
        print("\nProcessing wordclouds...")

        # Retrieve the queries configs to process from the Configs.
        if self.wordcloud_configs is None:
            print("@ No wordclouds found!")
            return
    
        # Iterate and build each query.
        for wordcloud in self.wordcloud_configs:

            # Process selected queries if specified. Otherwise, run all.
            if wordclouds and wordcloud.name not in wordclouds:
                continue

            try:
                wordcloud.run(self.datasets)
                print(f"* Screenplay `{wordcloud.name}` completed: {wordcloud.file}")

            except Exception as err:
                print(f"! Wordcloud `{wordcloud.name}` failed build: {err}")
