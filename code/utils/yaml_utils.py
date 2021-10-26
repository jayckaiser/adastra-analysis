import os
import yaml

# This module is currently unused.
# These were meant to allow deeper YAML customization in `configs.yml`.
# They have not been used or tested yet.

# https://stackoverflow.com/questions/5484016
def _os_join(loader, node):
    seq = loader.construct_sequence(node)
    return os.path.join(map(str, seq))

yaml.add_constructor('!JOIN', _os_join)

# 
def _and_join(loader, node):
    seq = loader.construct_sequence(node)
    return '(' + ') AND ('.join(map(str, seq)) + ')'

yaml.add_constructor('!AND', _and_join)

# 
def _or_join(loader, node):
    seq = loader.construct_sequence(node)
    return '(' + ') OR ('.join(map(str, seq)) + ')'

yaml.add_constructor('!OR', _or_join)


def load_yaml(filepath):
    """
    Standardized method to load a YAML file and instantiate a Configs.
    """
    with open(filepath, 'r') as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)