import os
import pandas as pd

def _renpy_to_rows(filepath):
    """
    Read a .rpy script and collect row information for each line.
    """
    file_name = os.path.splitext(
        os.path.basename(filepath)
    )[0]
    
    with open(filepath, 'r') as fp:
        lines = fp.readlines()
        
    rows = []
    for idx, line in enumerate(lines):
        rows.append( [file_name, idx, line] )
        
    return rows


def script_filepaths_to_df(script_filepaths, columns=['file', 'line_idx', 'raw']):
    """
    Given a directory of renpy scripts, return as a single Pandas DF.
    Collect the filename, line number, and raw text of each line.
    """
    
    file_dfs = []
    
    for filepath in script_filepaths:
        rows = _renpy_to_rows(filepath)
        
        # Create an individual DF to be joined later.
        df = pd.DataFrame(rows, columns=columns)
        file_dfs.append(df)
        
    return pd.concat(file_dfs)
