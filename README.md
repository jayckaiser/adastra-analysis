# adastra-analysis
TL;DR: What started as a goal to write the contents of the visual novel Adastra into screenplays has now become a ~two-week-long~ **month-long** project culminating in analyses and sand-boxing using text and images from the game. I've created an interactive set of scripts to create a cleaned dataset using the content that can be queried and plotted. In addition, I've codified a customizable interface for building wordclouds and formatted screenplays.


## Overview

Do you love the visual novel Adastra? Do you often reminisce about the time you spent there with best boy Amicus? Do you want to get a more intimate look at him and all the other kooky characters who try to kill you during your thirteen hours imprisoned in paradise?

By the gods, are you in luck! This code allows you to do the following:
- Collect and cleanse the internal script files of the game into a single JSONL dataset hydrated with metadata
- Query the dataset using SQL and output the results to disk
- Write the script files out as chapter-by-chapter screenplays, formatted by user-preference
- Recreate game illustrations and sprites as word clouds (customizable by speaker, file, etc.)
- Extract and save sentiment and aggregate statistics by speaker across chapter as relational plots

Note: I'm sharing this code as is. You should consider this repo both incomplete and a work-in-progress. This presumes you hold a basic knowledge of Python and running it locally. If there's enough interest, I'll expand upon the project and add a CLI, but please do not ask me for help resolving installation issues. StackOverflow will be far more helpful!

*(Please do reach out to me if you encounter a bug while using the library! I have **not** done enough testing.)*


## FYI

Adastra contains a total of 15,577 lines across 14 chapters of content, translating to 219,937 words in total. Given the mutual-exclusivity of optional choices and end-games, a player will consume roughly 180,907 words across a typical playthrough.

The average Harry Potter book is 250 words per page; the average Brandon Sanderson novel is 350. This means that the average playthrough of Adastra is between *516 and 723 pages* of content, depending on your preference of word-density.

I have reached out to Howly for permission to share the formatted full text contents of the game. Until I receive a response, I'm not including the screenplays or cleaned dataset in this library. It'll have to be generated from your end. If I receive permission in the future (or if someone can educate me on licensing to prove this content is already freely available to share), I will add these files to the repo.

Example wordclouds are found in `examples/wordclouds`. Example relational plots are found in `examples/relplots`. Example query outputs are found in `examples/queries`.

Read on to learn how you can play with this data yourself!

-----

## Setup

Create a new environment in which to play with this code (e.g. using venv). A `requirements.txt` file has been included to try to circumvent dependency errors.

Download the latest Linux version of Adastra. Unzip the directory and put it somewhere easily accessible. The location should be added to the configs file under `dataset_configs.adastra_directory`.

All logic for this library's outputs is derived from `configs.yml`. This is a single YAML file where you can specify exactly how you want to interact with the dataset, as well as how you want to output your queries, screenplays, relplots, and wordclouds. Below, I will document the structure of the file, its keys and their meanings, and suggestions for how to work with the library.

Example runs are already filled in. You can comment these out (`Ctrl + /` on most modern IDEs) and add your own, or customize them as you see fit.

Before you run any code, you need to populate a number of fields that specify where to output files on your machine:
- `dataset_configs.adastra_directory`
- `dataset_configs.adastra_datapath`
- `adastra_analytics.queries.output_directory`
- `adastra_analytics.screenplays.output_directory`
- `adastra_analytics.relplots.output_directory`
- `adastra_analytics.wordclouds.output_directory`

-----

## Scripts

`main.py` is the powerhouse to complete all processes defined in `configs.yml`. Before you can run additional processes, you must build the dataset.

To build the standard dataset:
>  ```
  python main.py --build-dataset
  ```
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


To build the data with extra NLP-specific fields:
>  ```
  python main.py --build-nlp-dataset
  ```
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

Once a dataset has been built, you can run processes from the configs file.

-----

## Run Adastra Analytics
The `--run` argument completes categories of processes from the `configs.yml` file that should be completed. You can choose one or more types to run a specific selection, or use `all` to run all.
```
python main.py --run {all, queries, screenplays, relplots, wordclouds}
```

-----

### Queries
SQL statements can be defined to query off the Adastra dataset and any other custom datasets defined in the configs. These are saved as JSON-lines.
```
python main.py --run queries
```

These are defined in `adastra_analytics.queries` in the configs file.
```
queries:
  output_directory: where should the JSONL files be saved?
  dataset_alias: how is the main Adastra dataset aliased in the queries?
  where [optional]: apply an optional SQL where filter to the dataset before any queries are run
  queries:
    - name: name of the output file to save the query result to
      sql: the SQL statement to run
    - ...
```

(See `examples/queries` for a preselected list of generated queries.)

-----

### Screenplays
Output the text contents of Adastra into cleaned and formatted screenplays, separated by chapter. Specify formatting by line-type using where-filters.
```
python main.py --run screenplays
```

These are defined in `adastra_analytics.screenplays` in the configs file.
```
screenplays:
  output_directory: where should the screenplays be saved?
  where [optional]: apply an optional SQL where filter to the dataset before any screenplays are created
  screenplays:
    - name: name of the output folder to save the screenplay files to
      justify: at how many characters should the text wrap to the next line?
      line_sep: how should lines be separated?
      formats:
        - where: where-filter to specify which lines are formatted in this style
          style [default "{line}"]: which parts of the row are included in the formatting, and how?
          justify [optional]: should this format use different formatting from the rest of the output?
          textwrap_offset [default 0]: how far should wrapped lines be offset from the left edge?
          parts:
            - name: name of column to include in the formatting (must be defined in `style`)
              strip_quotes [default False]: should wrapper quotes be removed?
              upper [default False]: should the text be cast to uppercase?
              lower [default False]: should the text be cast to lowercase?
              title [default False]: should the text be cast to title-case?
              offset [default 0]: how far should the line part be offset from the left edge?
              prefix: what text should be prefixed to the text?
              postfix: what text should be postfixed to the text?
            - ...
        - ...
    - ...
```

I've created three versions of outputs already. If someone has a better idea for how to best improve readability for the output, please let me know!

  - style1
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

  - style2
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

  - style3
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

-----

### Relational Plots
Create custom Seaborn relational plots based off of SQL statements queried off the Adastra dataset and any other custom datasets defined in the configs. Relplot arguments are entirely customizable based on standard Seaborn relplot kwargs.
```
python main.py --run replots
```

These are defined in `adastra_analytics.relplots` in the configs file.
```
relplots:
  output_directory: where should the JSONL files be saved?
  dataset_alias: how is the main Adastra dataset aliased in the queries?
  where [optional]: apply an optional SQL where filter to the dataset before any queries are run
  relplot_args:
    * these are universal kwargs to provide to all relplots
  relplots:
    - name: name of the output file to save the query result to
      relplot_args:
        * these are kwargs to provide to the relplot; they overwrite the universal kwargs defined above
      sql: the SQL statement to run
    - ...
```

(See `examples/relplots` for a preselected list of generated plots.)

-----

### Wordclouds
Save custom wordclouds based off of subsets of text and masked over specific images from the game (and elsewhere). These can be populated by lines from a specific where-filter of the data (e.g. only text from a specific file, only text spoken by Amicus, etc). These can even be specified down to specific scenes, if you know the file and line numbers.
```
python main.py --run wordclouds
```

These are defined in `adastra_analytics.wordclouds` in the configs file.

By default, a customized TF-IDF algorithm is used to generate word-frequencies for the wordclouds. I will not claim this has been coded correctly, but the wordclouds look nice, so I'm keeping it as is.

Wordplot arguments are entirely customizable based on `wordcloud.Wordcloud` kwargs. I've set up a nice set of defaults, but feel free to test further!

```
wordclouds:
  output_directory: where should the wordcloud images be saved?
  where [optional]: apply an optional SQL where filter to the dataset before any wordclouds are built
  documents_column: which column in the dataset should be used to build the wordclouds?
  filter_columns: which columns in the dataset are used in where-filter queries below?
  tfidf_args:
    * these are kwargs to provide to the CountVectorizer used to build the TF-IDF frequencies
  wordcloud_args:
    * these are universal wordcloud kwargs to apply to all wordclouds below
  wordclouds:
    - name: name of the output file to save the wordcloud to
      where: a where-filter to restrict which lines build the wordcloud
      wordcloud_args:
        * these are kwargs to provide to the wordcloud; they overwrite the universal kwargs defined above
    - ...
```

(See `examples/wordclouds` for a preselected list of generated clouds.)

-----

### Conclusion

This documentation is incomplete, but it's more than enough to get started! I'll continue to document and expand the project in the coming weeks. I've had a lot of fun building out this project, and I hope that someone else gets use out of all this work. Regardless, enjoy the wordclouds and screenplay files! Please reach out to `u/OrigamiOtter` for questions and feedback!

-----
