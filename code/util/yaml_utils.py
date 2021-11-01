import os
import yaml

from classes.dataset import Dataset
from classes.adastra_dataset import AdastraDataset

from classes.query import Query
from classes.relplot import Relplot
from classes.screenplay import Screenplay
from classes.wordcloud import Wordcloud



# These allow for more dynamic YAML customization in `configs.yml`.
def _os_path_join(loader, node):
    """
    # https://stackoverflow.com/questions/5484016
    """
    seq = loader.construct_sequence(node)
    return os.path.join(*seq)


def _and_join(loader, node):
    seq = loader.construct_sequence(node)
    return ' AND '.join(
        f"({ss})" for ss in seq 
    )


def _or_join(loader, node):
    seq = loader.construct_sequence(node)
    return ' OR '.join(
        f"({ss})" for ss in seq 
    )


def get_extended_yaml_loader():
    """
    Extend `yaml.SafeLoader` with additional constructors.
    """
    loader = yaml.FullLoader

    # String-join helpers
    loader.add_constructor('!PATH_JOIN', _os_path_join)
    loader.add_constructor('!AND', _and_join)
    loader.add_constructor('!OR', _or_join)

    # Run-process constructors
    loader.add_constructor('!Dataset', Dataset.yaml_constructor)
    loader.add_constructor('!AdastraDataset', AdastraDataset.yaml_constructor)
    
    loader.add_constructor('!Query'     , Query.yaml_constructor)
    loader.add_constructor('!Relplot'   , Relplot.yaml_constructor)
    loader.add_constructor('!Screenplay', Screenplay.yaml_constructor)
    loader.add_constructor('!Wordcloud' , Wordcloud.yaml_constructor)
    
    return loader


def load_yaml(filepath):
    """
    Standardized method to load a YAML file and instantiate a Configs.
    """
    with open(filepath, 'r') as fp:
        return yaml.load(fp, Loader=get_extended_yaml_loader())
