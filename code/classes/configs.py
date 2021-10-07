import os
import yaml

from ..dataset import Dataset
from ..query import Query


class Configs:
    CONFIGS_FILEPATH = '../configs.yml'

    def __init__(self, configs_filepath=CONFIGS_FILEPATH):
        self.configs_filepath = configs_filepath
        self.full_configs = self.load_configs(configs_filepath)


    @staticmethod
    def load_configs(configs_filepath):
        """
        Standardized method to load user-provided configs.
        """
        with open(configs_filepath, 'r') as fp:
            return yaml.load(fp, Loader=yaml.FullLoader)


    @staticmethod
    def check_keys(configs, keys):
        """
        Verify that all required dict keys are present to run a script.
        Raises an error prematurely to prevent unnecessary processing.
        """
        success = True

        for required_key in keys:
            if required_key not in configs:
                print(
                    f"Config key `{required_key}` is required to run this script!"
                )
                success = False

        if not success:
            raise Exception("Please fix missing keys and try again!")



    def parse_top_configs(self):
        """
        Extract universal configs information from the configs dict.
        Retrieve the relevant dataframe to be used for subsequent actions.
        
        New keys: [adastra_dir, data_filepath, *where_clause]
        """
        # Verify this universal configs are defined.
        if 'configs' not in self.full_configs:
            raise Exception(
                "All scripts require a 'configs' key defined in 'configs.yml'!"
            )
        top_configs = self.full_configs['configs']

        # Verify all necessary configs are defined.
        required_keys = [
            'adastra_dir', 'data_dir', 'use_nlp',
        ]
        self.check_keys(top_configs, keys=required_keys)

        # Save the path to the unzipped Adastra folder.
        self.adastra_dir = top_configs['adastra_dir']

        # Save the filepath to save/load the cleaned data.
        if top_configs['use_nlp']:
            filename = 'adastra_nlp.jsonl'
        else:
            filename = 'adastra.jsonl'

        self.adastra_filepath = os.path.join(
            top_configs['data_dir'], filename
        )

        # Save the optional where-clause to apply to any data defined in configs.yml.
        self.where_clause = top_configs.get('where')
        

    def get_adastra_data(self):
        """
        Build the inital adastra dataset, and apply optional where-filter.
        """
        adastra_data = Dataset(filepath=self.adastra_filepath)
        adastra_data = adastra_data.filter_where(self.where_clause)
        return adastra_data


    
    def get_queries_from_configs(self, dataset):
        """
        Extract and prepare SQL queries and dataset for processing.
        """
        # Retrieve the queries configs from the full configs; break if missing.
        queries_configs = self.full_configs.get('queries')
        if queries_configs is None:
            raise Exception(
                "`queries.py` requires a 'queries' key defined in 'configs.yml'!"
            )

        # Verify all necessary configs are defined.
        required_keys = [
            'output_dir', 'dataset_alias', 'files',
        ]
        self.check_keys(queries_configs, required_keys)

        # Iterate the files and yield each as a Query.
        for filename, query_params in queries_configs['files'].items():
            
            # Verify `sql` is present as a key.
            self.check_keys(query_params, ['sql'])

            # Retrieve required params and yield a Query object.
            output_dir    = queries_configs['output_dir']
            dataset_alias = query_params['dataset_alias']
            sql_query     = query_params['sql']
            where_clause  = query_params.get('where')

            output_filepath = os.path.join(
                output_dir, filename + '.jsonl'
            )
            query_obj = Query(
                filepath      = output_filepath,
                
                dataset       = dataset,
                where_clause  = where_clause,

                sql_query     = sql_query,
                dataset_alias = dataset_alias,
            )

            yield query_obj
