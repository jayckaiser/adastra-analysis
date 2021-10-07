import numpy as np
import pandas as pd

import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

from dataset import Dataset


def add_nlp_to_adastra_dataset(adastra_dataset):
    """
    Apply NLP on the lines to determine token and word counts.
    """

    # Build the spacy language model, and add the sentiment pipe.
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe('spacytextblob')

    # Copy the DF to prevent in-place transformations.
    data = adastra_dataset.data.copy()
    
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

    # Extract non-stop words
    content_word_lists = [
        [token.orth_.lower() for token in doc
            if not token.is_stop and not token.is_punct]
        for doc in docs
    ]
    
    # Save the new NLP information as columns.
    data['sentiment']          = sentiment_list
    data['subjectivity']       = subjectivity_list
    
    data['sentences']          = sentence_lists
    data['num_sentences']      = list(map(len, sentence_lists))
    
    data['words']              = word_lists
    data['num_words']          = list(map(len, word_lists))
    
    data['content_words']     = content_word_lists
    data['num_content_words'] = list(map(len, content_word_lists))
    
    return Dataset(data)
