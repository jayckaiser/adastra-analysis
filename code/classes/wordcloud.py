import gc

from classes.dataset import Dataset
from classes.run import Run

from util.tfidf_utils import get_term_freqs, filter_term_freqs, build_filtered_tfidf_word_freqs
from util.wordcloud_utils import word_freqs_to_wordcloud


class Wordcloud(Run):
    """
​
    """
    def __init__(
        self,

        name,
        file, 
        dataset,

        image,
        documents_col,
        where,

        countvectorizer_args,
        wordcloud_args,

    ):
        self.name = name
        self.file = file
        self.dataset = dataset

        self.image = image
        self.documents_col = documents_col
        self.where = where

        self.countvectorizer_args = countvectorizer_args
        self.wordcloud_args = wordcloud_args

        self.result = None


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

        self.prepare_directories(file)
        self.result.to_file(file)
        
        # Reset the wordcloud to prevent memory overflows.
        self.result = None
        gc.collect()
    