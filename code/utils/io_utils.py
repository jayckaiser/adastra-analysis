import gc
import os
import pandas as pd
import yaml

import matplotlib.pyplot as plt


# Data Input helpers
def load_dataframe(filepath):
    return pd.read_json(filepath, orient='records', lines=True)

def load_data(data_dir, nlp=False, is_read=False, drop_lists=False):
    """
    Standardized method for loading cleaned data.
    """
    # Specify whether to load the extended NLP dataframe.
    if nlp:
        filename = 'adastra_nlp.json'
    else:
        filename = 'adastra.json'

    # Load the dataframe, and filter on optional flags.
    filepath = os.path.join(data_dir, filename)
    df = pd.read_json(filepath, orient='records', lines=True)

    if is_read:
        df = df.query('is_read')

    # Note! PandasSQL does not support ListTypes. Manually remove these columns!
    if nlp and drop_lists:
        df = df.drop(['sentences', 'words', 'content_words'], axis=1)

    return df

    


# Data Output helpers
def _make_dir(filepath):
     os.makedirs( os.path.dirname(filepath), exist_ok=True )


def save_dataframe(dataframe, filepath):
    """
    Standardized method to write a Pandas DataFrame to disk.
    """
    _make_dir(filepath)
    dataframe.to_json(filepath, orient='records', lines=True)


def save_tsv(dataframe, filepath):
    """
    Standardized method to write a Pandas DataFrame to disk as TSV.
    """
    _make_dir(filepath)
    dataframe.to_csv(filepath, sep='\t', index=False)


def save_lines(lines, filepath):
    """
    Standardized method to write text lines to disk.
    """
    _make_dir(filepath)
    with open(filepath, 'w') as fp:
        fp.writelines(lines)


def save_wordcloud(wc, filepath):
    """
    Standardized method to save a wordcloud image to disk.
    """
    _make_dir(filepath)
    wc.to_file(filepath)


def save_figure(fig, filepath):
    """
    
    """
    fig.savefig(filepath, bbox_inches='tight')
    plt.close('all')
    gc.collect()




# Configs helpers
def load_yaml(filepath):
    """
    Generic yaml loader
    """
    with open(filepath, 'r') as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)

def get_config(config_name):
    """
    Helper to pull pathing information from the configs file.
    """
    config_path = '../configs/paths.yml'

    configs = load_yaml(config_path)
    return configs[config_name]

