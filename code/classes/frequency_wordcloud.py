import gc
import numpy as np
import pandas as pd

from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator

from utils.utils import prepare_directories


class FrequencyWordcloud:
    """
    
    """
    def __init__(
        self,

        frequencies,
        wordcloud_args,
        image_file,
    ):
        self.wordcloud = self.build_wordcloud(
            frequencies,
            wordcloud_args=wordcloud_args,
            image_file=image_file,

        )

    
    @staticmethod
    def wordcloud_constructor(loader, node):
        return FrequencyWordcloud(**loader.construct_mapping(node))


    @staticmethod
    def build_wordcloud(frequencies, wordcloud_args, image_file):
        """
        Create a word-frequency wordcloud from the user-provided arguments.
        
        Use a source image as a mask for its design.
        """
        image_mask = _get_image_mask(image_file)
        height, width, _ = image_mask.shape
        
        # Create the wordcloud shaped by the image.
        wc = WordCloud(
            mask=image_mask,
            width=width, height=height,
            **wordcloud_args
        ).generate_from_frequencies(frequencies)

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




def _get_image_mask(image_path):
    """
    Convert an image on disk to a numpy image mask.
    """
    image = Image.open(image_path)
    image_mask = np.array(image)
    return image_mask
