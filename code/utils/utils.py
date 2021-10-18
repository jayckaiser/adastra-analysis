import os

# These are arbitrary functions that didn't have another home.
# These may be moved in the future.

def prepare_directories(filepath):
    """
    Create missing directories and notify the user.
    """
    directory = os.path.dirname(filepath)

    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created new directory: `{directory}`")


def merge_dicts(dict1, dict2):
    """
    Simple helper to standardize merging argument dicts.
    """
    if dict1 is None:
        dict1 = {}

    if dict2 is None:
        dict2 = {}

    return {**dict1, **dict2}


def list_to_dict(list_, key):
    """
    
    """
    output = {}

    for dict_ in list_:
        dict_key = dict_.get(key)
        output[dict_key] = dict_
    
    return output
