import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.preprocessing import normalize

from dataset import Dataset


def _get_doc_freqs(term_freqs):
    """
    Convert a dataframe of term-freqs of tokens by line into doc-freq counts.
    """
    return np.array( term_freqs.astype(bool).sum() )



# JK:: Build another method to just SUM precomputed TF-IDF values.
# Compare to the output of the method below.
# How similar are they?



def get_term_freqs(data, index, doc_col, tfidf_args):
    """
    Convert a dataframe into term-freqs using CountVectorizer.

    The searchable index and documents column are arguments.
    Use user-provided TFIDF-arguments (none hard-coded).
    """
    # Build out the list of documents to feed to the vectorizer.
    documents = (
        data.copy()
            .reset_index()
            .set_index(index)
            [doc_col]
    )

    # Establish the CountVectorizer with the user-provided arguments.
    vectorizer = CountVectorizer(**tfidf_args)

    # Get the term frequencies and document frequencies.
    X = vectorizer.fit_transform(documents)
    features = vectorizer.get_feature_names_out()
    
    term_freqs = pd.DataFrame(
        X.toarray(),
        columns=features
    ).set_index(documents.index)

    return term_freqs


def filter_term_freqs(term_freqs, filters):
    """
    Subset term-freqs of a dataframe by specified filters.
    """
    # Build a new dataset with just the index.
    index = (
        term_freqs.index
            .to_frame(index=False)
    )
    index_cols = index.columns

    # Run the user-provided filter on this index.
    filtered_index = (
        Dataset(index.reset_index()).filter_where(filters)
            .set_index('index')
    )

    # Verify the filter hasn't truncated the dataset.
    if filtered_index.empty:
        raise Exception(f"! Filter query `{filters}` returned 0 rows!")

    # Filter the term freqs to only rows in user-provided filter.
    filtered_term_freqs = (
        term_freqs.reset_index()
            .drop(index_cols, axis=1)
            .filter(items=filtered_index.index, axis=0)
    )

    return filtered_term_freqs


def build_filtered_tfidf_word_freqs(
        term_freqs, filtered_term_freqs,
        smooth_idf=True
):
    """
    Combine term- and doc-freqs of a whole and filtered dataset
    into one set of word-freqs to pass to WordcloudImage.
    """
    # Build the document frequencies from the term frequencies.
    doc_freqs = _get_doc_freqs(term_freqs)
    filtered_doc_freqs = _get_doc_freqs(filtered_term_freqs)

    # Get all variables for calculating filtered IDFs.
    # Apply smoothing where required.
    len_term_freqs = len(term_freqs) + int(smooth_idf)
    len_filtered_term_freqs = len(filtered_term_freqs)

    doc_freqs += int(smooth_idf)
    
    # Calculate IDFs by combining filtered rows.
    filtered_inverse_doc_freqs = np.log(
        (len_term_freqs - len_filtered_term_freqs)
        / (doc_freqs - filtered_doc_freqs)
    ) + 1

    # Merge them into one TF-IDF and normalize.
    tfidfs = filtered_term_freqs * filtered_inverse_doc_freqs
    tfidfs = pd.DataFrame(
        normalize(tfidfs, norm='l2', axis=1)
    )

    # Sum into word frequency dicts of words to tfidf.
    word_frequencies = (
        pd.DataFrame(tfidfs.sum())
            .set_index(filtered_term_freqs.columns)
            .to_dict()
            [0]
    )

    # Filter out zero-count items (to allow word cloud repeat to actually work.)
    word_frequencies = {
        word: freq for word, freq in word_frequencies.items() if freq > 0 
    }

    return word_frequencies
