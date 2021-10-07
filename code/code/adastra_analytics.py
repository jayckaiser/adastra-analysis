import os
import yaml


class AdastraAnalytics:
    CONFIGS_FILEPATH = '../configs.yml'

    def __init__(self, configs_filepath=CONFIGS_FILEPATH, build_dataset=False):
        self.yaml_configs = self.load_yaml(configs_filepath)
        
        # Reset the string to follow.
        self.run_variables = self.get_universal_configs()

        # Create the dataset if manually triggered.
        adastra_datapath = self.run_variables.get('adastra_datapath')

        if build_dataset is True:
            adastra_dataset = cleaning.build_adastra_dataset(adastra_datapath)

        else:
            adastra_dataset = Dataset(adastra_datapath)
        
        # Declare all potential config options.
        self.query_configs = None
        self.wordcloud_configs = None
        self.relplot_configs = None
        self.screenplay_configs = None


    def get_universal_configs(self):
        """
        Extract universal configs information from the configs dict.
        Retrieve the relevant dataframe to be used for subsequent actions.
        
        New keys: [adastra_dir, data_filepath, *where_clause]
        """
        # Verify we have enough configs to get started.
        self.check_keys(
            ['configs', 'adastra_analytics']
        )

        # Reset the string to follow.
        self.reset_rope().follow('adastra_analytics')

        # Verify all necessary configs are defined.
        self.check_keys(
            ['adastra_dir', 'data_dir', 'use_nlp',]
        )

        # Record the paths to program IO.
        self.adastra_directory = self.get('adastra_directory')
        self.output_directory  = self.get('data_directory')
        
        # Save the filepath to save/load the cleaned data.
        use_nlp = self.get('use_nlp')

        if use_nlp:
            filename = 'adastra_nlp.jsonl'
        else:
            filename = 'adastra.jsonl'

        self.adastra_datapath = os.path.join(
            self.output_directory, filename
        )
        

    def get_adastra_data(self):
        """
        Build the inital adastra dataset, and apply optional where-filter.
        """
        # Reset the string to follow.
        self.reset().get('adastra_analytics')

        # Add an optional where if present.
        filters =  self.get('filter')

        adastra_data = Dataset(
            filepath=self.adastra_datapath,
            filters=filters,
        )
        return adastra_data


    def get_datasets(self):
        # Reset the string to follow.
        self.reset().get('adastra_analytics').get('datasets')

        if 

  

    @staticmethod
    def load_yaml(filepath):
        """
        Standardized method to load a YAML file.
        """
        with open(filepath, 'r') as fp:
            return yaml.load(fp, Loader=yaml.FullLoader)


    def check_keys(self, keys):
        """
        Verify that all required dict keys are present to run a script.
        Raises an error prematurely to prevent unnecessary processing.
        """
        success = True

        for key in keys:
            if key not in self.rope:
                print(
                    f"Config key `{key}` is required to run this script!"
                )
                success = False

        if not success:
            raise Exception("Please fix missing keys and try again!")



    def get(self, key):
        return self.configs.get(key)

    def follow(self, key):
        self.rope = self.string.rope(key)

    def reset_rope(self):
        self.rope = self.yaml_configs.copy()
        return self.rope
