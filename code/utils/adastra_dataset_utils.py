import os
import re

import pandas as pd


ADASTRA_RENPY_SCRIPT_FILES = [
    'a1s1.rpy', 'a1s2.rpy', 'a1s3.rpy', 'a1s4.rpy',
    'a1s5.rpy', 'a1s6.rpy', 'a1s7.rpy',
    'a2s1.rpy', 'a2s2.rpy', 'a2s3.rpy',
    'a3s1.rpy', 'a3s2.rpy',
    'end_game1.rpy', 'end_game2.rpy',
]


def build_adastra_data(
        adastra_directory,
        renpy_script_files=ADASTRA_RENPY_SCRIPT_FILES,
        main_character='Marco',
    ):
    """
    Load the DataFrame from text and complete all transformations.
    """

    # Convert all Renpy script files into a single unioned DataFrame.
    data = renpy_files_to_dataframe(adastra_directory, renpy_script_files)
    
    # JK:: Why did we do this again?
    data = data.reset_index()
    
    # Categorize the text, extract the speaker (if present), and cleanse the line.
    data[['category', 'speaker', 'line']] = data.apply(
        lambda x: extract_text_information(x['raw'], main_character=main_character),
        axis=1,
        result_type='expand'
    )

    # Add logic flags to allow cleaner filtering later.
    data[['is_renpy', 'is_choice', 'is_read', 'has_speaker', 'is_branch']] = data.apply(
        lambda x: add_filter_flags(x['category'], x['raw']),
        axis=1,
        result_type='expand'
    )
    
    # Convert character aliases to their actual names.
    data['speaker'] = data.apply(
        lambda x: conform_speaker(x['speaker'], main_character=main_character),
        axis=1
    )
    
    # Final ordering of the columns.
    final_select = [
        'file', 'line_idx',
        'category', 'speaker',
        'line',
        'is_renpy', 'is_choice', 'is_read', 'has_speaker', 'is_branch',
        'raw',
    ]
    data = data[final_select]

    return data



###### FUNCTIONS FOR RAW DATA LOADING
def _renpy_file_to_dataframe(filepath):
    """
    Read a .rpy script and collect row information for each line.
    """
    columns = ['file', 'line_idx', 'raw']

    file_name = os.path.splitext(
        os.path.basename(filepath)
    )[0]
    
    with open(filepath, 'r') as fp:
        raw_line = fp.readlines()
        
    rows = []
    for line_idx, line in enumerate(raw_line):
        rows.append( [file_name, line_idx, line] )

    return pd.DataFrame(rows, columns=columns)


def renpy_files_to_dataframe(adastra_directory, renpy_filenames):
    """
    Given a directory of renpy scripts, return as a single Pandas DF.
    Collect the filename, line number, and raw text of each line.
    """
    
    file_dataframes = []
    for file in renpy_filenames:

        # Build the full path to the Renpy script file.
        renpy_filepath = os.path.join(
            adastra_directory, 'game', file
        )

        dataframe = _renpy_file_to_dataframe(renpy_filepath)
        file_dataframes.append(dataframe)
        
    return pd.concat(file_dataframes)



######### FUNCTIONS FOR CLEANING
def _cleanse_line(line, main_character):
    """
    Cleanse the extracted lines to remove formatting.
    """
    # Strip the line, just in case.
    line = line.strip()
    
    # Clean up formatting characters.
    line = line.replace('\\'  , '')  # Remove escape characters.
    line = line.replace('[mc]', main_character)  # Standardize MC name.
    line = re.sub(r'{/?i}'    , '*', line)  # Convert italics to Markdown.
    line = re.sub(r'{cps=\d+}', '' , line)  # Remove scroll speed formatting.
    
    return line

def extract_text_information(text, main_character):
    """
    Categorize each line based on rules involving special characters, keywords, and regex matches.
    Extract relevant metadata and clean the lines as needed.
    """

    DIALOGUE_ALIAS_REGEX       = re.compile(r'^(?P<char>[a-z]+) "(?P<line>.*)"$')
    DIALOGUE_NAME_REGEX        = re.compile(r'^"(?P<char>.*?)" "(?P<line>.*)"$')
    DIALOGUE_UNSPECIFIED_REGEX = re.compile(r'^"(?P<line>".+")"$')
    DIALOGUE_INTERNAL_REGEX    = re.compile(r'^"(?P<line>.+)"$')
    CHOICE_PLAYER_REGEX        = re.compile(r'^"(?P<line>.+)":$')

    CHOICE_CONDITION_KEYWORDS = [
        'if ', 'else:'
    ]

    RENPY_KEYWORDS = [
        'ease', 'hide',  'jump', 'label', 'menu', 
        'pause', 'play', 'queue', 'return', 'scene',
        'scene', 'show', 'stop', 'window', 'with',
    ]


    ### Standardize formatting to make the extraction process easier.
    text = _cleanse_line(text, main_character=main_character)
    
    ### Create categories and isolate speaker for each line.
    category = 'unknown'
    speaker = None
    line = text
    
    # Some categories are obvious.
    if text.startswith('#'):
        category = 'renpy_comment'
    elif text.startswith("$"):
        category = 'renpy_python'
    elif any(text.startswith(x) for x in RENPY_KEYWORDS) or text == '':
        category = 'renpy_keyword'
    elif any(text.startswith(x) for x in CHOICE_CONDITION_KEYWORDS):
        category = 'choice_condition'
    
    # Others need regex to pull out the necessary pieces.
    else:
        is_dialogue_alias_match       = DIALOGUE_ALIAS_REGEX.match(text)
        is_dialogue_name_match        = DIALOGUE_NAME_REGEX.match(text)
        is_dialogue_unspecified_match = DIALOGUE_UNSPECIFIED_REGEX.match(text)
        is_dialogue_internal_match    = DIALOGUE_INTERNAL_REGEX.match(text)
        is_choice_player_match        = CHOICE_PLAYER_REGEX.match(text)
        
        # Test each regex, and if True, extract relevant fields.
        if is_dialogue_alias_match:
            speaker  = is_dialogue_alias_match.group('char')
            line     = is_dialogue_alias_match.group('line')
            category = 'dialogue_alias'
        elif is_dialogue_name_match:
            speaker  = is_dialogue_name_match.group('char')
            line     = is_dialogue_name_match.group('line')
            category = 'dialogue_name'
        elif is_dialogue_unspecified_match:
            speaker  = 'speaker_unspecified'
            line     = is_dialogue_unspecified_match.group('line')
            category = 'dialogue_unspecified'
        elif is_dialogue_internal_match:
            speaker  = 'internal_narration'
            line     = is_dialogue_internal_match.group('line')
            category = 'dialogue_internal'
        elif is_choice_player_match:
            line     = is_choice_player_match.group('line')
            category = 'choice_player'
    
    return (category, speaker, line)


def add_filter_flags(category, text):
    """
    Add flag columns for easier filtering downstream.
    """    
    # Specify if a line is internal to Renpy.
    is_renpy = category.startswith('renpy_')
    
    # Specify which lines indicate a crossroads.
    is_choice = category.startswith('choice_')

    # Specify when it's actual text to be read.
    is_read = category.startswith('dialogue_')
    
    # Specify when a character actually speaks the line.
    has_speaker = is_read and category not in ('dialogue_unspecified', 'dialogue_internal')
    
    # Optional (branching) content is tab-indented.
        # Note: This is custom to Adastra, not all RenPy games!
        # * conditional   = 0 space indent; branch content = 4 space indent
        # * player_choice = 4 space indent; branch content = 8 space indent
    is_branch = text.startswith(' ' * 4) and not is_choice
    
    return (is_renpy, is_choice, is_read, has_speaker, is_branch)


def conform_speaker(speaker, main_character):
    """
    Normalize speaker names using the predefined map.
    """

    CHARACTERS_MAP = {
        'a'  : 'amicus',
        'm'  : main_character,
        'unk': '?????',
        'com': 'computer',
        'c'  : 'cassius',
        'ca' : 'cato',
        'al' : 'alexios',
        'v'  : 'virginia',
        'n'  : 'neferu',
        'mon': 'monitor',
        'sc' : 'scipio',
        'me' : 'meera',
    }

    # Join the speaker aliases to their proper name.
    if speaker is None:
        return None

    return CHARACTERS_MAP.get(speaker, speaker).lower() 
