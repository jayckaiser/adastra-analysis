import gc
import numpy as np
import pandas as pd

from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator


def _get_image_mask(image_path):
    """
    Convert an image on disk to a numpy image mask.
    """
    image = Image.open(image_path)
    image_mask = np.array(image)
    return image_mask


def word_freqs_to_wordcloud(word_freqs, image, wordcloud_args):
    """
    Create a word-frequency wordcloud from the user-provided arguments.
    
    Use a source image as a mask for its design.
    """
    image_mask = _get_image_mask(image)
    height, width, _ = image_mask.shape
    
    # Create the wordcloud shaped by the image.
    wc = WordCloud(
        mask=image_mask,
        width=width, height=height,
        **wordcloud_args
    ).generate_from_frequencies(word_freqs)

    # Recolor the wordcloud to match the image.
    image_colors = ImageColorGenerator(image_mask)
    wc = wc.recolor(color_func=image_colors)

    return wc