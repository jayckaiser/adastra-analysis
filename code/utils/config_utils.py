import os
import yaml

import pandas as pd
import pandasql as psql

from classes.query import Query
from utils.io_utils import load_dataframe


CONFIGS_PATH = '../configs.yml'

def load_configs(configs_filepath=CONFIGS_PATH):
    """
    Standardized method to load user-provided configs.
    """
    with open(configs_filepath, 'r') as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)



# Helper methods involving dictionaries and keys.
def merge_dicts(x, y):
    """
    Merge two dictionaries, preferring arguments from y.
    (Python 3.9 has this logic built-in. I'm not using 3.9.)
    """
    return {**x, **y}


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



# Dataset load w/ variables helpers
def filter_where(data_, dataset_alias, where):
    """
    Apply a where-clause to the dataset, using the alias provided in the PandaSQL query.
    """
    if where is None:
        return data_

    exec(f"{dataset_alias} = data_")
    return psql.sqldf(f"""
        select * from {dataset_alias}
        where {where}
    """)


def load_dataset_with_configs(configs, variables):
    """
    Standardized method to load the cleaned adastra dataset with defined configs/variables.
    """
    # Load in the JSONL dataset defined at `variables.data_filepath`.
    data_filepath = variables['data_filepath']
    data_ = load_dataframe(data_filepath)
    print(
        f"Loaded dataset from `{data_filepath}`."
    )

    # Apply a custom filter if specified.
    where = configs.get('where')
    data_ = filter_where(data_, 'data_', where)

    return data_



# Config checks and extractions.
def parse_main_configs(full_configs):
    """
    Extract universal configs information from the configs dict.
    Retrieve the relevant dataframe to be used for subsequent actions.
    """
    # Verify this universal configs are defined.
    if 'configs' not in full_configs:
        raise Exception(
            "All scripts require a 'configs' key defined in 'configs.yml'!"
        )
    configs = full_configs['configs']

    # Verify all necessary configs are defined.
    required_configs = [
        'adastra_dir', 'data_dir', 'use_nlp',
    ]
    check_keys(configs, keys=required_configs)

    # Build the filepath to save/load the cleaned data.
    if configs['use_nlp']:
        filename = 'adastra_nlp.jsonl'
    else:
        filename = 'adastra.jsonl'

    data_filepath = os.path.join(configs['data_dir'], filename)

    return {
        'adastra_dir'  : configs['adastra_dir'],
        'data_filepath': data_filepath,
    }


def parse_configs_datasets(full_configs):
    """
    Extract and convert dataset configs to Pandas DataFrames.
    """
    datasets = []

    # End prematurely if no custom datasets are predefined.
    if 'datasets' not in full_configs:
        print("No custom datasets defined.")
        return datasets

    configs = full_configs['datasets']

    # Iterate the datasets configs and add to the return-dict.
    for dataset_name, dataset_params in configs.items():

        # Verify all necessary configs are defined.
        required_configs = [
            'columns', 'data',
        ]
        verify_required_keys(dataset_params, keys=required_configs)

        # Create a dataframe based on the data and save to datasets.
        data_ = pd.DataFrame(
            list(dataset_params['data'].items()),
            columns=dataset_params['columns']
        )


        datasets.append({
            'dataset_alias': dataset_name,
            'dataset': data_,
        })

    return datasets



def parse_configs_queries(full_configs, variables):
    """
    Extract and prepare SQL queries and dataset for processing.
    """
    # Verify this script's key is defined.
    if 'queries' not in full_configs:
        raise Exception(
            "`queries.py` requires a 'queries' key defined in 'configs.yml'!"
        )
    configs = full_configs['queries']

    # Verify all necessary configs are defined.
    required_configs = [
        'output_dir', 'dataset_alias', 'files',
    ]
    verify_required_keys(configs, required_configs)

    # Load in the cleaned dataset defined at the path in 'variables'.
    data_ = load_dataset_with_configs(configs, variables)

    # Iterate the files and yield each as a Query.
    for file, query_params in configs['files'].items():
        
        # Verify `sql` is present as a key.
        verify_required_keys(query_params, ['sql'])

        # Apply a where-filter if specified.
        where = query_params.get('where')
        data_ = filter_where(data_, 'data_', where)

        filepath = os.path.join(
            configs['output_dir'], file + '.jsonl'
        )
        query_obj = Query(
            filepath      = filepath,
            dataset       = data_,
            dataset_alias = configs['dataset_alias'],
            sql           = query_params['sql'],
        )
        yield query_obj

    




def parse_configs(script):
    """
    Main method for extracting configs and preparing scripts.
    """
    # Load the configs as a dict.
    full_configs = load_configs()

    # Verify the configs key is actually present, and retrieve.
    variables = parse_configs_main(full_configs['configs'])

    # queries.py
    if 'queries' == script:

        # Load custom datasets
        datasets = parse_configs_datasets(full_configs)

        queries_configs = parse_configs_queries(full_configs, variables)




