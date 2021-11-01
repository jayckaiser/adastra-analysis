import gc
import pandas as pd

from classes.dataset import Dataset

from util.utils import prepare_directories
from util.tfidf_utils import get_term_freqs, filter_term_freqs, build_filtered_tfidf_word_freqs
from util.wordcloud_utils import word_freqs_to_wordcloud

class Wordcloud:
    """
​
    """
    def __init__(
        self,

        name,
        file, 
        image,
        documents_col,
        where,
        dataset,

        countvectorizer_args,
        wordcloud_args,

    ):
        self.name = name
        self.file = file
        self.image = image
        self.documents_col = documents_col
        self.where = where
        self.dataset = dataset

        self.countvectorizer_args = countvectorizer_args
        self.wordcloud_args = wordcloud_args

        self.result = None


    @staticmethod
    def wordcloud_constructor(loader, node):
        return Wordcloud(**loader.construct_mapping(node, deep=True))


    def build_wordcloud(self, datasets):
        """
        
        """
        _data = Dataset(**self.dataset).build_dataset(datasets=datasets)

        _term_freqs = get_term_freqs(
            data=_data.copy(),
            doc_col=self.documents_col,
            countvectorizer_args=self.countvectorizer_args
        )

        # The documents are sourced by a subset of rows in the dataset.
        # Use these to build TF-IDF word frequencies.
        _filtered_term_freqs = filter_term_freqs(
            _term_freqs,
            where=self.where
        )
        
        _word_freqs = build_filtered_tfidf_word_freqs(
            _term_freqs, _filtered_term_freqs
        )
        
        self.result = word_freqs_to_wordcloud(
            _word_freqs,
            image=self.image,
            wordcloud_args=self.wordcloud_args
        )
        

    def to_disk(self, file=None):
        """
        
        """
        file = file or self.file

        prepare_directories(file)
        self.result.to_file(file)
        
        # Reset the wordcloud to prevent memory overflows.
        self.result = None
        gc.collect()
    