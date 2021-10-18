import gc
import numpy as np
import pandas as pd

from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator


from utils.utils import prepare_directories


class WordcloudImage:
    """
    Class to simplify creating Wordcloud images.

    (This is named as such to avoid naming collisions with `wordcloud.Wordcloud`.)
    """
    def __init__(
        self,
        word_frequencies,
        image_filepath,
        wordcloud_args,
    ):
        self.word_frequencies = word_frequencies
        
        self.image_filepath = image_filepath
        self.wordcloud_args = wordcloud_args

        self.wordcloud = self.build_wordcloud()


    @staticmethod
    def get_image_mask(image_path):
        """
        Convert an image on disk to a numpy image mask.
        """
        image = Image.open(image_path)
        image_mask = np.array(image)
        return image_mask


    def build_wordcloud(self):
        """
        Create a word-frequency wordcloud from the user-provided arguments.
        
        Use a source image as a mask for its design.
        """
        image_mask = self.get_image_mask(self.image_filepath)
        height, width, _ = image_mask.shape
        
        # Create the wordcloud shaped by the image.
        wc = WordCloud(
            mask=image_mask,
            width=width, height=height,
            **self.wordcloud_args
        ).generate_from_frequencies(self.word_frequencies)

        # Recolor the wordcloud to match the image.
        image_colors = ImageColorGenerator(image_mask)
        wc = wc.recolor(color_func=image_colors)

        return wc


    def to_disk(self, filepath):
        """
        Save the wordcloud to disk as an image, then reset memory.
        """
        prepare_directories(filepath)
        self.wordcloud.to_file(filepath)
        
        # Reset the wordcloud to prevent memory overflows.
        self.wordcloud = None
        gc.collect()
