import textwrap
from string import Formatter

from classes.dataset import Dataset
from utils.utils import merge_dicts, prepare_directories

class Screenplay:
    """
​
    """
    def __init__(
        self,

        data,
        columns=None,
        where=None,
        sql=None,
        dataset_alias=None,
        datasets=None,

        # screenplay_args=None,
        categories={},
        justify=None,
        line_sep='\n',
    ):
        # Screenplays are really graphical extensions of Datasets.
        self.data = Dataset(
            data,
            columns=columns,
            where=where,
            sql=sql,
            dataset_alias=dataset_alias,
            datasets=datasets,
        ).get_data()

        # 
        self.screenplay_rows = self.build_screenplay_rows(
            self.data,
            # screenplay_args=screenplay_args,
            categories=categories,
            justify=justify,
        )

        self.line_sep = line_sep


    @staticmethod
    def screenplay_constructor(loader, node):
        return Screenplay(**loader.construct_mapping(node))


    @staticmethod
    def build_screenplay_rows(data, categories, justify=None):
        """
        Convert all lines in a dataset into a specified format.
        """
        _data = data.copy()

        # For each format, subset the dataframe and format each line.
        for category_name, categories_configs in categories.items():

            # Check the format-keys, and build optional parts-configs.
            categories_configs.check_keys(
                ['where', 'style']
            )
            where = categories_configs.get('where')
            style = categories_configs.get('style')
            _formatting = categories_configs.get('formatting', {})

            _textwrap_offset = categories_configs.get('textwrap_offset', 0)
            _add_bar = categories_configs.get('add_bar', False)
            _justify = categories_configs.get('justify', justify)

            # Subset the screenplay dataset and format those lines.
            _screenplay_subset = (
                _data.copy()
                    .filter_where(where)
            )
            
            # Perform transformations on the lines, based on the config logic provided.
            _screenplay_subset['line'] = _screenplay_subset.apply(
                lambda row: build_formatted_line(
                    row,
                    _formatting,
                    style=style,
                    justify=_justify,
                    textwrap_offset=_textwrap_offset,
                    add_bar=_add_bar,
                ),
                axis=1
            )

            # Update the original dataset with those changes.
            merged = _data.merge(
                _screenplay_subset[['file', 'line_idx', 'line']],
                how='left',
                on=['file', 'line_idx'],
            )
            merged['line'] = merged['line_y'].fillna(merged['line_x'])
            merged = merged.drop(['line_x', 'line_y'], axis=1)

            _data = Dataset(merged)
            print(f"* `{category_name}` logic applied.", flush=True, end='\r')

        return _data


    def to_disk(self, filepath):
        """
        Write a given column to a filepath as text.
        """
        prepare_directories(filepath)

        lines = self.screenplay_rows['line'].tolist()

        with open(filepath, 'w') as fp:
            fp.write( self.sep.join(lines) )
        



# Internal helper methods for `build_formatted_line`.
def _textwrap_wrap(string, justify):
    """
    Custom instantiation of textwrap.wrap() to account for new lines in string.
    """
    output = []

    for line in string.splitlines():
        justified = textwrap.wrap(
            line, justify,
            break_long_words=False, replace_whitespace=False
        )

        output.extend(justified)

    return output


def _format_line_part(line_part, configs):
        """
        Format a part of a line with using custom parameters.
        """
        # Set defaults in case otherwise undefined.
        default_configs = {
            'strip_quotes': False,
            'upper': False,
            'lower': False,
            'title': False,
            'offset': 0,
            'prefix': None,
            'postfix': None,
        }

        # Merge with any defined configs.
        line_part_configs = merge_dicts(default_configs, configs)

        # Begin the formatting, using the defined variables.
        strip_quotes = line_part_configs.get('strip_quotes')
        upper        = line_part_configs.get('upper')
        lower        = line_part_configs.get('lower')
        title        = line_part_configs.get('title')
        offset       = line_part_configs.get('offset')
        prefix       = line_part_configs.get('prefix')
        postfix      = line_part_configs.get('postfix')

        formatted = line_part

        # Strip quotes if specified.
        if strip_quotes:
            formatted = formatted.strip('"')

        # Complete text casing first.
        if upper:
            formatted = formatted.upper()
        if lower:
            formatted = formatted.lower()
        if title:
            formatted = formatted.title()

        # Apply prefixes or postfixes if specified.
        if prefix:
            formatted = prefix + formatted
        if postfix:
            formatted = formatted + postfix

        # Apply whitespace offsetting.
        if offset:
            formatted = (' ' * offset) + formatted

        return formatted



def _justify_text(text, justify, textwrap_offset=0):
    """
    Justify the text to a given size, accouting for custom offset on wrapped lines.
    """        
    # Apply inital justification.
    justified_lines = _textwrap_wrap(
        text,
        justify
    )

    # If the wrapped lines need offset, this must be removed from the justify size.
    if textwrap_offset:

        # If the line is too short to justify, ignore special processing.
        if len(justified_lines) > 1:

            # Extract the first line, rejoin and rejustify accounting for offset.
            first_line = justified_lines[0]
            remaining_text = ' '.join(justified_lines[1:])
            remaining_lines = _textwrap_wrap(
                remaining_text,
                justify - textwrap_offset
            )
        
            # Apply the offsets to the start of the remaining lines.
            remaining_lines = [
                (' ' * textwrap_offset) + line
                for line in remaining_lines
            ]

            # Recombine as a single set.
            justified_lines = [first_line] + remaining_lines

    # Strip excess whitespace from the ends of the lines.
    justified_lines = [line.rstrip() for line in justified_lines]
    
    # Join the lines into a single string value.
    return '\n'.join(justified_lines)



def _extract_format_strings(string):
    """
    Extract format-string variable names.

    Example:
    - "{speaker}\n{line}" -> ['speaker', 'line']
    """
    return [
        fname
        for _, fname, _, _ in Formatter().parse(string)
        if fname
    ]



# Main method applied across rows in the dataset.
def build_formatted_line(
    row,
    formatting_configs,
    style,
    justify=None,
    textwrap_offset=0,
    add_bar=False,
):
    """
    Full logic for converting a single row into a formatted line.
    """
    line_parts = {}

    # Apply the config logic to each part of the line.
    for line_part_name in _extract_format_strings(style):
        
        # Extract the line part text from the row.
        line_part = row[line_part_name]

        # Complete each line part configs, defaulting to no formatting if unspecified.
        line_part_configs = formatting_configs.get(line_part_name)
        formatted = _format_line_part(line_part, line_part_configs)

        # Add the transformed line part back to the dictionary.
        line_parts[line_part_name] = formatted

    # Combine the format strings into the style.
    formatted_line = style.format(**line_parts)

    # Apply textwrap justify to the formatted_line.
    if justify:
        formatted_line = _justify_text(
            formatted_line,
            justify,
            textwrap_offset=textwrap_offset,
        )

    # Add a bar if specified.
    if add_bar:
        if justify:
            bar = '-' * justify
        else:
            bar = '-' * 10
        
        formatted_line = bar + '\n' + formatted_line

    return formatted_line
