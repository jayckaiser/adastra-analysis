import textwrap


def dataframe_to_script_lines(df, script_method):
    """
    Convert a cleaned Adastra DF to lines to be printed.
    """
    
    script_lines = []
    
    prev_row = {}  # Hold onto the previous row each loop (used for v3 formatting).
    for _, row in df.iterrows():
        
        script_lines.append(
            script_method(row, prev_row)
        )
        prev_row = row
        
    return script_lines


def row_to_script_lines_v1(row, prev_row=None):
    """
    Abstracted method to print rows in book-form.
    (Designed around The Cursed Child.)
    """
    # Account for optional content and branching when displaying.
    if row['is_optional']:
        spaces_prefix = " " * 8
    elif row['is_choice']:
        spaces_prefix = " " * 4
    else:
        spaces_prefix = ""
        
    # Handle choices
    if row['is_choice']:
        return f"{spaces_prefix}{row['line']}\n"
        
    # Handle dialogue/narration
    if row['has_speaker']:
        return f"{spaces_prefix}{row['speaker'].upper()}\n{spaces_prefix}  {row['line']}\n"
    else:
        return f"{spaces_prefix}{row['line']}\n"


def row_to_script_lines_v2(row, prev_row=None, justify_size=80, indent_size=4):
    """
    Abstracted method to print rows in book-form.
    (Designed by sight after not liking v1.)
    """
    # Account for optional content and branching when displaying.
    if row['is_optional']:
        spaces_prefix = " " * 8
    elif row['is_choice']:
        spaces_prefix = " " * 4
    else:
        spaces_prefix = ""
        
    # Handle choices
    if row['is_choice']:
        return f"[BRANCH] {row['line']}\n"
        
    # Handle dialogue/narration
    justify_indent_size = len(spaces_prefix) + indent_size
    justify_indent = " " * justify_indent_size
    
    if row['has_speaker']:
        full_text = f"{justify_indent}{row['speaker'].upper()}: {row['line']}"
        
        first_line = textwrap.wrap(full_text, width=justify_size)[0]
        remaining_text = full_text[len(first_line):]
        remaining_lines = textwrap.wrap(remaining_text, width=(justify_size - justify_indent_size))
        
        return (
            first_line
            + ''.join(f'\n{justify_indent}{line.strip()}' for line in remaining_lines)
            + '\n'
        )
    else:
        full_text = f"{spaces_prefix}{row['line']}"
        
        first_line = textwrap.wrap(full_text, width=justify_size)[0]
        remaining_text = full_text[len(first_line):]
        remaining_lines = textwrap.wrap(remaining_text, width=(justify_size - justify_indent_size))
        
        return (
            first_line
            + ''.join(f'\n{spaces_prefix}{line.strip()}' for line in remaining_lines)
            + '\n'
        )


def row_to_script_lines_v3(row, prev_row, justify_size=75, dialogue_size=45):
    """
    Abstracted method to print rows in book-form.
    (Designed to look like a screenplay. My favorite.)
    """
    script_line = ""
    
    # Handle ends of optional tracks.
    if row is not None and (row['is_optional'] == False) and prev_row.get('is_optional', False):
        script_line += ('-' * justify_size) + '\n\n'
    
    
    # Handle choices
    if row['is_choice']:
        script_line += f"{'-' * justify_size}\n[BRANCH] {row['line']}\n"
        
    # Handle dialogue/narration
    elif row['has_speaker']:
        center_offset = (justify_size - dialogue_size) // 2
        
        speaker_line = (' ' * center_offset) + row['speaker'].upper()
        justified_lines = textwrap.wrap(row['line'], dialogue_size)
        
        
        script_line += (
            ' ' * center_offset
            + speaker_line
            + ''.join(
                f'\n{" " * center_offset}{line.strip()}'
                for line in justified_lines
            )
        ) + '\n'
            
    else:
        justified_lines = textwrap.wrap(row['line'], justify_size)
        
        script_line += (
            '\n'.join(
                line.strip() for line in justified_lines
            )
        ) + '\n'

    return script_line
