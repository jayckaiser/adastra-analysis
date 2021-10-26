import numpy as np
import pandas as pd

import spacy
from spacytextblob.spacytextblob import SpacyTextBlob


def nlp_augment_adastra_data(adastra_data):
    """
    Apply NLP on the lines to add sentiment, tokenization, etc.
    """

    # Define the characters used to join lists into single strings for output.
    sentence_join_str = '\n'
    word_join_str     = ' '

    # Build the spacy language model, and add the sentiment pipe.
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe('spacytextblob')

    # Copy the DF to prevent in-place transformations.
    data = adastra_data.copy()
    
    # Pipe the lines through the spaCy document-creator.
    docs = list(
        nlp.pipe( data['line'] )
    )
    
    
    # Build up the new columns' values as lists.

    # Add sentiment (polarity) and subjectivity, from `spacytextblob`.
    sentiment_list = list(map(
        lambda doc: doc._.polarity,
        docs
    ))
    
    subjectivity_list = list(map(
        lambda doc: doc._.subjectivity,
        docs
    ))
    
    # Isolate sentences
    sentences_list = list(map(
        lambda doc: [sent.text for sent in doc.sents],
        docs
    ))
    num_sentences_list = list(map(len, sentences_list))
    sentences_list = list(map(
        lambda sents: sentence_join_str.join(sents),
        sentences_list
    ))
    
    # Extract lists of actual words
    words_list = list(map(
        lambda doc: [token.orth_ for token in doc
            if not token.is_punct],
        docs
    ))
    num_words_list = list(map(len, words_list))
    words_list = list(map(
        lambda words: word_join_str.join(words),
        words_list
    ))

    # Extract non-stop words
    content_words_list = list(map(
        lambda doc: [token.orth_.lower() for token in doc
            if not token.is_stop and not token.is_punct],
        docs
    ))
    num_content_words_list = list(map(len, content_words_list))
    content_words_list = list(map(
        lambda words: word_join_str.join(words),
        content_words_list
    ))

    
    # Save the new NLP information as columns.
    data['sentiment']          = sentiment_list
    data['subjectivity']       = subjectivity_list
    
    data['sentences']          = sentences_list
    data['num_sentences']      = num_sentences_list
    
    data['words']              = words_list
    data['num_words']          = num_words_list
    
    data['content_words']     = content_words_list
    data['num_content_words'] = num_content_words_list
    
    return data
