import gc
import os
import pandas as pd
import yaml

import matplotlib.pyplot as plt
import seaborn as sns


# Data Input helpers
# def _read_dataframe(filepath):
    # return pd.read_json(filepath)

def load_data(data_dir, nlp=False, is_read=False):
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
    df = pd.read_json(filepath)

    if is_read:
        df = df.query('is_read')

    return df

    


# Data Output helpers
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


def save_plot(
    data,
    filepath,
    x, y, hue,
    palette,
    kind = 'scatter',
    figsize=(16,10),
    axhline = None,
    **kwargs
):
    # Set to darkgrid (to see Cassius).
    sns.set_theme(style='darkgrid')

    # Make the directory if non-existent.
    _make_dir(filepath)

    # Create the figure, using kwargs for customization.
    plt.figure()
    sns.relplot(
        x=x, y=y,
        hue=hue,
        palette=palette,
        kind=kind,
        data=data,
        **kwargs
    )

    # Add a custom horizontal line if specified.
    if axhline is not None:
        plt.axhline(axhline, linestyle='--', color='black', alpha=0.5)

    fig = plt.gcf()
    fig.set_size_inches(*figsize)
    fig.savefig(filepath, bbox_inches='tight')

    # Force garbage collection (idk pyplot doesn't release memory?)
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

