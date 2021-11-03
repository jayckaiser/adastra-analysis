# adastra-analysis
TL;DR: What started as a goal to write the contents of the visual novel Adastra into screenplays has now become a ~two-week-long~ **two-month-long** project culminating in a system to dynamically interact with text and images from Adastra. Through a set of scripts, you can parse the game's files into a cleaned dataset and other generated files. These include formatted screenplays, wordclouds, and relation plots.

![amicus](/examples/wordclouds/sprites/amicus.png)

-----

# Overview

Do you love the visual novel Adastra? Do you often reminisce about the time you spent there with best boy Amicus? Do you want to get a more intimate look at him and all the other kooky characters who try to kill you during your thirteen hours imprisoned in paradise?

By the gods, are you in luck! This code allows you to do the following:
- Collect and cleanse the internal script files of the game into a single JSONL dataset hydrated with metadata
- Query the dataset using SQL and output the results to disk
- Write the script files out as chapter-by-chapter screenplays, formatted by user-preference
- Recreate game illustrations and sprites as word clouds (customizable by speaker, file, etc.)
- Extract and save sentiment and aggregate statistics by speaker across chapter as relational plots

Note: I'm sharing this code as is. You should consider this repo both incomplete and a work-in-progress. This presumes you hold a basic knowledge of Python and running it locally; please do not ask me for help resolving installation issues. StackOverflow will be far more helpful!

*Please do reach out to me if you encounter a bug while using the library! I have **not** done enough testing.*


# FYI

Adastra contains a total of 15,577 lines across 14 chapters of content, translating to 219,937 words in total. Given the mutual-exclusivity of optional choices and end-games, a player will consume roughly 180,907 words across a typical playthrough.

The average Harry Potter book is 250 words per page; the average Brandon Sanderson novel is 350. This means that the average playthrough of Adastra is between *516 and 723 pages* of content, depending on your preference of word-density.

I have reached out to Howly for permission to share the formatted full text contents of the game. Until I receive a response, I'm not including the screenplays or cleaned dataset in this library. It'll have to be generated from your end. If I receive permission in the future (or if someone can educate me on licensing to prove this content is already freely available to share), I will add these files to the repo.

Example wordclouds are found in `examples/wordclouds`. Example relational plots are found in `examples/relplots`. Example query outputs are found in `examples/queries`.

Read on to learn how you can play with this data yourself!

-----

![islandday](examples/wordclouds/backgrounds/islandday.png)

-----


# Setup

Create a new environment in which to play with this code (e.g. using `venv`). A `requirements.txt` file has been included to try to circumvent dependency errors.

Download the latest Linux version of Adastra. Unzip the directory and put it somewhere easily accessible.

All logic for this library's outputs is derived from a single YAML config file. This is where you can specify exactly how you want to interact with the dataset, as well as how you want to output your queries, relplots, screenplays, and wordclouds. By default, this is defined within the library at `adastra_analysis_configs.yaml`; you can specify another path using `--configs`.

Example runs are already filled into the configs. You can comment these out (`Ctrl + /` on most modern IDEs) and add your own, or customize them as you see fit.

Below, I will document the structure of the file, its structure, and suggestions for how to interact with the library.

-----

![alexandcassiuskiss](/examples/wordclouds/illustrations/alexandcassiuskiss.PNG)

-----



# Scripts

All functionality of this library is completed using the following command:
```
python -m adastra_analysis
```
Attempt to run this command before changing any configs or running any subroutines.


## Build

Before you can run additional processes, you must build the datasets. There are two classes of dataset logic defined:
* `AdastraDataset`: main logic for collecting and transforming raw Adastra game files into a DataFrame
* `Dataset`: any other DataFrame built from either provided data, read in from a filepath, or built using SQL transformations on a preexisting DataFrame

One example of each dataset has been predefined: `adastra`, an `AdastraDataset`; and `characters`, a mapping of character names to color codes used in plotting


The `adastra` dataset contains the text of each line, its index, and metadata for querying the its contents. By default, the dataset contains these columns:

| Column | Type | Description |
| ------ | ---- | ----------- |
| file | str | name of source file |
| line_idx | int | line number of file |
| category | enum | line category (among a predefined set of enumerations) |
| speaker | str | character/source of the line (includes 'internal_narration' and 'speaker_unspecified') |
| line | str | cleaned text of the line |
| is_renpy | bool | is the line internal Ren'Py-logic? |
| is_choice | bool | is the line a split to multiple branches (a player choice or conditional Python logic)? |
| is_read | bool | is the line text read by the player? |
| has_speaker | bool | is the line spoken by a named speaker (not internal narration or an unspecified speaker)? |
| is_branch | bool | is the line an optional branch (delineated by a choice)? |
| raw | str | raw text of the line |


Additionally, I have built optional NLP functionality that can extend the dataset. These are the additional NLP columns added:

| Column | Type | Description |
| ------ | ---- | ----------- |
| sentiment | [-1, 1] | sentiment of the line (negative to positive) |
| subjectivity | [0, 1] | subjectivity (strength) of the sentiment |
| sentences | str | sentences in the line, joined by newlines |
| num_sentences | int | number of sentences |
| words | str | non-punctuation words in the line, joined by spaces |
| num_words | int | number of extracted words |
| content_words | str | non-stop/filler words in the line, joined by spaces |
| num_content_words | int | number of extracted content words |


To extend the dataset with NLP, set the `use_nlp` flag in the dataset's configs to `True`.

Once a dataset is built and saved, it can be queried in runs.

-----

![nefandcat2](examples/wordclouds/illustrations/nefandcat2.PNG)

-----

## Run
There are four types of runs I have defined in this library. The functionality of each is defined in the configs file.

To run the processes:

```
python -m adastra_analysis run [--queries] [--relplots] [--screenplays] [--wordclouds]
```

If no arguments are specified after `run`, all runs in the configs file will be run.

*Regardless of what is selected, run types will be completed in order of fastest-to-complete to slowest-to-complete (in the order listed above).*


All runs are specified under separate headers in the configs file. Under each run name, a sandbox area is provided for YAML anchors that define variables used in the runs. (These are ignored by the YAML parser.)

-----

### Queries
Define SQL statements to query against the datasets. The outputs of these are saved as JSON-lines.

Names of specific queries can be provided on the command line. Otherwise, all are run.
```
python -m adastra_analysis run --queries [query1 [query2 ...]]
```

Each run should be prefaced with `!Query`.
```
queries:

  [YAML DEFINITIONS SANDBOX]

  queries:

    - !Query
      name   : key to query, accessible via `--queries name`
      file   : output path for Query .jsonl file
      dataset: dataset of the query
```

*(See `examples/queries` for a predefined list of generated queries.)*



-----

### Relational Plots
Create custom relational plots using SQL queried against the datasets. These are saved as PNG files.

Names of specific relplots can be provided on the command line. Otherwise, all are run.
```
python -m adastra_analysis run --relplots [relplot1 [relplot2 ...]]
```

These are defined in `adastra_analytics.relplots` in the configs file.

Relplot arguments are entirely customizable based on standard Seaborn relplot kwargs. See [here](https://seaborn.pydata.org/generated/seaborn.relplot.html) for the Relplot source code (to get a feel for the kwargs).

```
relplots:

  [YAML DEFINITIONS SANDBOX]

  relplots:

    - !Relplot:
      name           : key to query, accessible via `--relplots name`
      file           : output path for Relplot .png file
      dataset        : dataset for the relplot
      relplot_args   : custom `seaborn.relplot` kwargs to define the relplot
      figsize        : (default (16, 10))  ; the size of the relplot figure
      title          : (default None)      ; a custom title for the relplot
      style          : (default 'darkgrid'); the background style of the relplot
      axhline        : (default None)      ; height of a horizontal line applied to the relplot
      remove_outliers: (default False)     ; apply smoothing to the output by filtering y data within within three-sigmas

```

*(See `examples/relplots` for a predefined list of generated plots.)*


![a1s7_sentiment](examples/relplots/sentiment/a1s7.png)


-----

### Screenplays
The text contents of Adastra are cleaned into formatted screenplays, separated by chapter. Specify formatting by line-type using where-filters. Screenplays are saved as TXT files in a specified folder.

Names of specific screenplays can be provided on the command line. Otherwise, all are run.
```
python -m adastra_analysis run --screenplays [screenplay1 [screenplay2 ...]]
```

These are defined in `adastra_analytics.screenplays` in the configs file.
```
screenplays:

  [YAML DEFINITIONS SANDBOX]

  screenplays:

    - !Screenplay
      name          : key to query, accessible via `--screenplays screenplay_style1`
      folder        : output subfolder under {output_directory}
      dataset       : dataset for the screenplay
      justify       : how wide should the output be (justify-width)
      line_sep      : how should lines be separated
      file_col      : name of the column to split into files based on unique values
      screenplay_col: name of the column to output formatting to

      contexts:
        - name               : name of the category; only used to track progress
          where              : where-clause to filter which lines use the given category style
          justify            : (optional) custom justify-width that overwrites the screenplay-global one defined above
          style              : shape of the output with columns used (i.e. "{column1}: {column2}")
          textwrap_offset    : (default 0); how far should wrapped text be indented; defaults to 0

          columns:
            - name           : name of the column to be inserted into the style
              screenplay_args: formatting arguments to apply the the text of the column

```

*(I've created three versions of outputs already. If someone has a better idea for how to best improve readability for the output, please let me know!)*

#### style1
```
Amicus turns his head to look at me again, then looks away, letting out
another groan.

AMICUS
  "Ohh, my stomach. What did you do?"

MARCO
  "Exactly what you did to me."

I hold up my taser, turning it in the light so that the wolf can fully see
it.

Amicus stares at it for a moment before letting his face fall back to the
floor of the deck.

AMICUS
  "Oh Gods, I feel like I'm on fire...did you use it at full power? What
the hell is wrong with you!?"
```

#### style2
```
Amicus turns his head to look at me again, then looks away, letting out
another groan.

AMICUS: "Ohh, my stomach. What did you do?"

MARCO: "Exactly what you did to me."

I hold up my taser, turning it in the light so that the wolf can fully see
it.

Amicus stares at it for a moment before letting his face fall back to the
floor of the deck.

AMICUS: "Oh Gods, I feel like I'm on fire...did you use it at full power?
    What the hell is wrong with you!?"
```

#### style3
```
Amicus turns his head to look at me again, then looks away, letting out
another groan.

               AMICUS
               "Ohh, my stomach. What did you do?"

               MARCO
               "Exactly what you did to me."

I hold up my taser, turning it in the light so that the wolf can fully see
it.

Amicus stares at it for a moment before letting his face fall back to the
floor of the deck.

               AMICUS
               "Oh Gods, I feel like I'm on fire...did you
               use it at full power? What the hell is wrong
               with you!?"
```

*(I have chosen to forgo including any example screenplays here until I receive express permission from one of the creators of Adastra. These will have to be generated on your end for the time being.)*


-----


### Wordclouds
Save custom wordclouds based off of subsets of dialogue text and masked over specific images (both from the game and external). These can be populated by lines from a specific where-filter of the data (e.g. only text from a specific file, only text spoken by Amicus, etc), or even by specific scenes if you know the file and line numbers. Wordclouds are saved as PNG files.

Names of specific wordclouds can be provided on the command line. Otherwise, all are run.
```
python -m adastra_analysis run --wordclouds [wordcloud1 [wordcloud2 ...]]
```

These are defined in `adastra_analytics.wordclouds` in the configs file.

By default, a customized TF-IDF algorithm is used to generate word-frequencies for the wordclouds. The TF portion is built using sklearn's `CountVectorizer`; this is customizable via user-provided kwargs.  See [here](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.CountVectorizer.html) for the CountVectorizer source code (to get a feel for the kwargs).

*Note: I will not claim this has been coded correctly, but the wordclouds look nice, so I'm keeping it as is.*

Wordcloud arguments are entirely customizable based on `wordcloud.Wordcloud` kwargs. I've set up a nice set of defaults, but feel free to test further! See [here](https://github.com/amueller/word_cloud/blob/master/wordcloud/wordcloud.py) for the Wordcloud source code (to get a feel for the kwargs).

```
wordclouds:

  [YAML DEFINITIONS SANDBOX]

  wordclouds:

  - !Wordcloud
     name                : key to query, accessible via `--wordclouds wordcloud1`
     file                : output path for wordcloud
     dataset             : dataset to build term frequencies out of for the wordcloud
     image               : path to image mask
     where               : where-clause to subset term frequencies used in the wordcloud
     documents_col       : text column to use for building term frequencies
     countvectorizer_args: `sklearn.CountVectorizer` kwargs to use when building the term frequencies
     wordcloud_args      : `wordcloud.Wordcloud` kwargs to define the wordcloud
```

*(See `examples/wordclouds` for a predefined list of generated clouds.)*

-----

### Conclusion

This documentation is incomplete, but it's more than enough to get started! I'll continue to document and expand the project in the coming weeks. I've had a lot of fun building out this project, and I hope that someone else gets use out of all this work. Regardless, enjoy the wordclouds I've shared! Please reach out to `u/OrigamiOtter` for questions and feedback!

![amicusend](/examples/wordclouds/illustrations/amicusend.png)
