import numpy as np
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator


def make_wordcloud_image(
    word_frequencies,
    image_path,
    **kwargs
):
    # Collect the image of the picture to paint.
    coloring_image = Image.open(image_path)
    coloring_image_array = np.array(coloring_image)
    width, height = coloring_image.size
    
    # Create the wordcloud shaped by the image.
    wc = WordCloud(
        mask=coloring_image_array,
        width=width, height=height,
        **kwargs
    ).generate_from_frequencies(word_frequencies)

    # Recolor the wordcloud to match the image.
    image_colors = ImageColorGenerator(coloring_image_array)
    wc = wc.recolor(color_func=image_colors)

    return wc
