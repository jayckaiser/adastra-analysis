import numpy as np
import pandas as pd

import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize



def nlp_transform_df(df_):
    """
    Apply NLP on the lines to determine token and word counts.
    """

    # Build the spacy language model, and add the sentiment pipe.
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe('spacytextblob')


    # Copy the DF to prevent in-place transformations.
    df = df_.copy()
    
    # Pipe the lines through the spaCy document-creator.
    docs = list(nlp.pipe(df['line']))
    
    # Ignore tokens. They're super easy to recollect if need be.
    
    # Add sentiment (polarity) and subjectivity, from `spacytextblob`.
    sentiment_list = [
        doc._.polarity for doc in docs
    ]
    
    subjectivity_list = [
        doc._.subjectivity for doc in docs
    ]
    
    # Isolate sentences
    sentence_lists = [
        [sent.text for sent in doc.sents] 
        for doc in docs
    ]
    
    # Extract lists of actual words
    word_lists = [
        [token.orth_ for token in doc
            if not token.is_punct]
        for doc in docs
    ]
    
    # # Isolate non-stop/filler lemmas
    # content_lemma_lists = [
    #     [token.lemma_.lower() for token in doc
    #         if not token.is_stop and not token.is_punct]
    #     for doc in docs
    # ]

    # Isolate non-stop word
    content_word_lists = [
        [token.orth_.lower() for token in doc
            if not token.is_stop and not token.is_punct]
        for doc in docs
    ]
    
    # Save the new NLP information as columns.
    df['sentiment']          = sentiment_list
    df['subjectivity']       = subjectivity_list
    
    df['sentences']          = sentence_lists
    df['num_sentences']      = list(map(len, sentence_lists))
    
    df['words']              = word_lists
    df['num_words']          = list(map(len, word_lists))
    
    df['content_words']     = content_word_lists
    df['num_content_words'] = list(map(len, content_word_lists))
    
    return df





# https://towardsdatascience.com/86518cdcb61f
def lines_to_tfs(
    df_,
    index=['file', 'speaker', 'line_idx', 'is_optional'],
    doc_col='line',
    **kwargs
)-> pd.DataFrame:

    # Build out the list of documents to feed to the vectorizer.
    documents = (
        df_.copy()
            .reset_index().set_index(index)
            [doc_col]
            .apply(lambda x: x if isinstance(x, str) else ' '.join(x))
    )

    # Gather TF and IDF counts from the documents.
    vectorizer = CountVectorizer(
        stop_words='english',
        ngram_range=(1,1),
        **kwargs
    )

    # Get the term frequencies and apply the counts to the documents index.
    X = vectorizer.fit_transform(documents)
    features = vectorizer.get_feature_names_out()
    
    tf = pd.DataFrame(
        X.toarray(),
        columns=features
    ).set_index(documents.index)
    
    return tf


def get_queried_tf_word_frequencies(tf, filter_query, smooth_idf=True):

    # Infer the inverse document frequency, applying smoothing if specified.
    len_tf = len(tf) + int(smooth_idf)
    doc_freq = np.array( tf.astype(bool).sum() )
    doc_freq += int(smooth_idf)

    # Filter the dataframe to only rows that fit the filter query.
    query_tf = tf.query(filter_query)

    if len(query_tf) == 0:
        raise Exception(f"!!! Filter query `{filter_query}` returned 0 rows!")

    len_query_tf = len(query_tf)
    query_doc_freq = np.array( query_tf.astype(bool).sum() )

    # Calculate IDF, acknowledging combined query rows.
    idf = np.log(
        (len_tf - len_query_tf)
        / (doc_freq - query_doc_freq)
    ) + 1

    # Merge them into one TF-IDF and normalize.
    raw_tfidf = query_tf * idf
    normalized_tfidf = pd.DataFrame(
        normalize(raw_tfidf, norm='l2', axis=1)
    )

    # Sum into word frequency dicts of words to tfidf.
    word_frequencies = (
        pd.DataFrame(normalized_tfidf.sum())
            .set_index(tf.columns)
            .to_dict()
            [0]
    )

    # Filter out zero-count items (to allow word cloud repeat to actually work.)
    word_frequencies = {
        word: freq for word, freq in word_frequencies.items() if freq > 0 
    }

    return word_frequencies
