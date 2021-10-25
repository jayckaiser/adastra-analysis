import os

from classes.dataset import Dataset

from utils.relplot_utils import build_relplot, relplot_to_disk
from utils.screenplay_utils import format_rows_to_lines
from utils.tfidf_utils import filter_term_freqs, build_filtered_tfidf_word_freqs
from utils.wordcloud_utils import build_wordcloud, wordcloud_to_disk



def query_main(
    query_name,

    adastra_dataset,
    dataset_alias,
    where,
    datasets,
    sql,

    output_file,
):
    """
    Method with all query logic to pass to AA.
    """
    try:
        # Filter the adastra dataset further if specified.
        # Add to the dictionary of datasets.
        datasets = datasets.copy() 
        datasets[dataset_alias] = Dataset(adastra_dataset) \
            .filter_where(where)

        # Complete the SQL query on the datasets.
        output_dataset = Dataset.query_psql(
            datasets,
            sql_query=sql
        )

        # Output the results to the specified disk location.
        output_dataset.to_jsonl(output_file)
        print(f"* Query `{query_name}` completed: {output_file}")

    except Exception as err:
        print(f"! Query `{query_name}` failed: {err}")



def relplot_main(
    relplot_name,

    adastra_dataset,
    dataset_alias,
    where,
    datasets,
    sql,

    relplot_args,
    figsize,
    title,
    axhline,
    remove_outliers,

    output_file,
):
    """
    Method with all relplot logic to pass to AA.
    """
    try:
        # Filter the adastra dataset further if specified.
        # Add to the dictionary of datasets.
        datasets = datasets.copy()

        datasets[dataset_alias] = Dataset(adastra_dataset) \
            .filter_where(where)

        # Run the SQL statement on the datasets.
        output_dataset = Dataset.query_psql(
            datasets,
            sql_query=sql
        )

        # Build the relplot based on the given arguments.
        output_relplot = build_relplot(
            output_dataset,
            relplot_args=relplot_args,
            title=title,
            figsize=figsize,
            axhline=axhline,
            remove_outliers=remove_outliers
        )

        # Output the results to the specified disk location.
        relplot_to_disk(output_relplot, output_file)
        print(f"* Relplot `{relplot_name}` completed: {output_file}")
    
    except Exception as err:
        print(f"! Relplot `{relplot_name}` failed: {err}")



def screenplay_main(
    screenplay_name,

    adastra_dataset,
    where,
    add_columns,

    categories,
    justify,
    line_sep,

    output_folder,
):
    """
    Method with all screenplay logic to pass to AA.
    """
    try:
        # Filter the adastra dataset further if specified.
        # Add new columns if specified.
        screenplay_dataset = adastra_dataset \
            .filter_where(where) \
            .add_columns(add_columns)

        # Transform the dataset's lines into formatted lines.
        formatted_screenplay_dataset = format_rows_to_lines(
            screenplay_dataset,
            categories=categories,
            justify=justify,
        )

        # Iterate the file names and output each as a separate file.
        for file in formatted_screenplay_dataset['file'].unique():
            formatted_screenplay_subset = formatted_screenplay_dataset \
                .filter_where(f'file = "{file}"')

            # 
            output_filepath = os.path.join(output_folder, file + '.txt')
            formatted_screenplay_subset.to_txt(output_filepath, 'line', sep=line_sep)

        print(f"* Screenplay `{screenplay_name}` completed: {output_folder}")
    
    except Exception as err:
        print(f"! Screenplay `{screenplay_name}` failed: {err}")



def wordcloud_main(
    wordcloud_name,

    term_freqs,
    where,

    image_file,
    wordcloud_args,
    
    output_file,
):
    """
    Method with all wordcloud logic to pass to AA.
    """
    try:
        # The documents are sourced by a subset of rows in the dataset.
        # Use these to build TF-IDF word frequencies.
        filtered_term_freqs = filter_term_freqs(
            term_freqs,
            filters=where
        )
        
        word_freqs = build_filtered_tfidf_word_freqs(
            term_freqs, filtered_term_freqs
        )

        wc = build_wordcloud(
            word_freqs,
            image_filepath=image_file,
            wordcloud_args=wordcloud_args
        )

        # Output the results to the specified disk location.
        wordcloud_to_disk(wc, output_file)
        print(f"* Wordcloud `{wordcloud_name}` completed: {output_file}")
    
    except Exception as err:
        print(f"! Wordcloud `{wordcloud_name}` failed: {err}")