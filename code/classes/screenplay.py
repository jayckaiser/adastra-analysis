import os
import textwrap

from dataclasses import dataclass

from classes.dataset import Dataset
from util.utils import prepare_directories


class Screenplay:
    """
​
    """
    def __init__(
        self,

        name,
        folder, 
        dataset,

        justify,
        line_sep,
        file_col,
        screenplay_col,
        contexts,

    ):
        self.name = name
        self.folder = folder
        self.dataset = dataset

        self.justify = justify
        self.line_sep = line_sep
        self.file_col = file_col
        self.screenplay_col = screenplay_col
        self.contexts = contexts

        self.result = None


    @staticmethod
    def screenplay_constructor(loader, node):
        return Screenplay(**loader.construct_mapping(node, deep=True))


    def build_screenplay(self, datasets):
        """
        
        """
        _data = Dataset(**self.dataset).build_dataset(datasets=datasets)


        # For each format, subset the dataframe and format each line.
        for context_config in self.contexts:

            context = Context(**context_config)
            
            # Subset the screenplay dataset and format those lines.
            _screenplay_subset = Dataset.filter_where(_data, context.where)
            
            # Perform transformations on the lines, based on the config logic provided.
            _screenplay_subset[self.screenplay_col] = _screenplay_subset.apply(
                lambda row: build_formatted_line(
                    row,
                    context.columns,
                    style=context.style,
                    justify=context.justify or self.justify,
                    textwrap_offset=context.textwrap_offset,
                    add_bar=context.add_bar,
                ),
                axis=1
            )

            # Update the original dataset with those changes.
            col_x = f'{self.screenplay_col}_x'
            col_y = f'{self.screenplay_col}_y'

            merged = _data.merge(
                _screenplay_subset[['file', 'line_idx', self.screenplay_col]],
                how='left',
                on=['file', 'line_idx'],
            )
            merged[self.screenplay_col] = (
                merged[col_y]
                    .fillna(merged[col_x])
            )
            _data = merged.drop([col_x, col_y], axis=1)
            
            print(f"* `{context.name}` logic applied.", flush=True, end='\r')

            self.result = _data


    def to_disk(self, folder=None):
        """
        
        """
        folder = folder or self.folder

        # Iterate the file names and output each as a separate file.
        for file in self.result[self.file_col].unique():
            where = f'{self.file_col} = "{file}"'

            file_data = Dataset.filter_where(self.result, where)
            file_lines = file_data[self.screenplay_col].tolist()

            file_path = os.path.join(folder, file + '.txt')
            prepare_directories(file_path)
            with open(file_path, 'w') as fp:
                fp.write(
                    self.line_sep.join(file_lines)
                )
            


@dataclass
class Context:
    name: str
    where: str
    style: str
    columns: list

    justify: int = None
    textwrap_offset: int = 0
    add_bar: bool = False


@dataclass
class ColumnConfigs:
    name: str
    screenplay_args: dict


@dataclass
class ScreenplayArgs:
    strip_quotes: bool = False
    upper: bool = False
    lower: bool = False
    title: bool = False
    offset: int = 0
    prefix: str = ""
    postfix: str = ""



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
        screenplay_args = ScreenplayArgs(**configs)

        formatted = line_part

        # Strip quotes if specified.
        if screenplay_args.strip_quotes:
            formatted = formatted.strip('"')

        # Complete text casing first.
        if screenplay_args.upper:
            formatted = formatted.upper()
        if screenplay_args.lower:
            formatted = formatted.lower()
        if screenplay_args.title:
            formatted = formatted.title()

        # Apply prefixes or postfixes if specified.
        if screenplay_args.prefix:
            formatted = screenplay_args.prefix + formatted
        if screenplay_args.postfix:
            formatted = formatted + screenplay_args.postfix

        # Apply whitespace offsetting.
        if screenplay_args.offset:
            formatted = (' ' * screenplay_args.offset) + formatted

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


# Main method applied across rows in the dataset.
def build_formatted_line(
    row,
    column_configs,
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
    for config in column_configs:
        column_config = ColumnConfigs(**config)
        
        # Extract the line part text from the row.
        column = row[column_config.name]

        # Complete each line part configs, defaulting to no formatting if unspecified.
        formatted = _format_line_part(column, column_config.screenplay_args)

        # Add the transformed line part back to the dictionary.
        line_parts[column_config.name] = formatted

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
