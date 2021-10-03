import os
import pandas as pd
import yaml


# Data IO helpers
def read_dataframe(filepath):
    return pd.read_json(filepath)


def _make_dir(filepath):
     os.makedirs( os.path.dirname(filepath), exist_ok=True )

def save_dataframe(dataframe, filepath):
    """
    Standardized method to write a Pandas DataFrame to disk.
    """
    _make_dir(filepath)
    dataframe.to_json(filepath)

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


# Configs helpers
def _load_yaml(filepath):
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

    configs = _load_yaml(config_path)
    return configs[config_name]

def get_wordcloud_list():
    config_path = '../configs/wordclouds.yml'
    return _load_yaml(config_path)
