# adastra-analysis
TL;DR: What started as a goal to write the contents of the visual novel Adastra into screenplays has now become a two-week-long project culminating in analyses and sand-boxing using text the game. I've created an interactive set of scripts to play with the content and output it as cleaned text files and word cloud images.

Adastra contains a total of 15,577 lines across 14 chapters of content, translating to 219,937 words. Given the mutual-exclusivity of optional choices and end-games, a player will consume roughly 180,907 words across a typical playthrough.

The average Harry Potter book is 250 words per page; the average Brandon Sanderson novel is 350. This means that the average playthrough of Adastra is between *516 and 723 pages* of read content, depending on your preference of word-density.

I have reached out to Howly for permission to share the formatted full text contents of the game. Because I have not yet received a response, I'm not including the screenplays or cleaned dataset in this library. It'll have to be generated from your end. If I receive permission in the future (or if someone can educate me on licensing to prove this content is already free-to-share), I will add these files to the repo.

Example wordclouds I've generated are found in `examples/wordclouds`. Analytics graphs are found in `examples/analytics`. Read on to learn how you can play with this data yourself!





### Overview

Do you love the visual novel Adastra? Do you often reminisce about the time you spent there with best boy Amicus? Do you want to get a more intimate look at him and all the other kooky characters who try to kill you during your thirteen hours imprisoned in paradise?

By the gods, are you in luck! This code allows you to do the following:
- Collect and cleanse the internal script files of the game into a single JSONL dataset hydrated with metadata
- Search game text by keyword/key-phrase
- Query the dataset using SQL
- Write the script files out as easily-consumable chapter-by-chapter screenplays
- Recreate game illustrations and sprites as word clouds (customizable by speaker, file, etc.)
- Extract and graph sentiment and aggregate statistics by speaker across chapter

Note: I'm sharing this code as is. You should consider this repo both incomplete and a work-in-progress. This presumes you hold a basic knowledge of Python and running it locally. If there's enough interest, I'll expand upon the project and add a CLI, but please do not ask me for help resolving installation issues. StackOverflow will be far more helpful!





### Setup

Create a new environment in which to play with this code (e.g. using venv). A `requirements.txt` file has been included to try to circumvent dependency errors.

Download the latest Linux version of Adastra. Unzip the directory and put it somewhere easily accessible.

Before you run any code, alter each key in `configs/paths.yml` to match your own environment.
- ***adastra_dir***: the path to the unzipped Adastra game files (i.e. `Adastra-17-linux`)
- ***data_dir***: where should the `adastra.json` and `adastra_nlp.json` dataframes be stored?
- ***screenplays_dir***: where should formatted screenplay files be saved?
- ***wordclouds_dir***: where should word cloud images be saved?
- ***analytics_dir***: where should sentiment and aggregate graphs be saved?
- ***queries_dir***: where should interactive query results be saved?





### Scripts

There are a number of script files present, each of which has distinct functionality. Some are dependent on others upstream. I'd recommend running 00 and 01 in numerical order to ensure no dependencies are missed.


- ***00_cleaning.py***   
Read the unzipped script files and save as a cleaned DataFrame to `{data_dir}/adastra.json`. Note: this must be run before any other scripts!

| Column | Type | Description |
| ------ | ---- | ----------- |
| file | str | name of source file |
| line_idx | int | line number of file |
| category | enum | line category (predefined set) |
| speaker | str | character/source of the line (includes 'internal' and 'unspecified') |
| line | str | cleaned text of the line |
| is_renpy | bool | is the line internal Ren'Py-logic? |
| is_choice | bool | is the line a split to multiple paths (a player choice or conditional Python logic)? |
| is_read | bool | is the line read as text by the player? |
| has_speaker | bool | is the line spoken by a named speaker (not internal or unspecified)? |
| is_optional | bool | is the line an optional path (delineated by a choice)? |
| raw | str | raw text of the line |



- ***01_nlp.py***  
Extend the cleaned dataframe with additional NLP fields and save to `{data_dir}/adastra_nlp.json`. Tokenization and content-word extraction use `spaCy` and its smallest model (`en_core_web_sm`); sentiment and subjectivity use `textblob`. Note: several other scripts are dependent on the output of this!

| Column | Type | Description |
| ------ | ---- | ----------- |
| sentiment | [-1, 1] | sentiment of the line (negative to positive) |
| subjectivity | [0, 1] | subjectivity (strength) of the sentiment |
| sentences | List[str] | sentences in the line |
| num_sentences | int | number of sentences |
| words | List[str] | non-punctuation words in the line |
| num_words | int | number of extracted words |
| content_words | List[str] | non-stop/filler words in the line |
| num_content_words | int | number of extracted content words |


- ***find.py***  
Find all lines that contain a specified phrase. Note that this search is case-insensitive.
  - `python find.py "the gods"`
  - `python find.py love`


- ***show.py***  
Show the full DataFrame contents of a specified query. This uses Pandas DataFrame query syntax.
  - `python show.py "speaker == 'amicus'"`
  - `python show.py "speaker.isin(['amicus', 'marco']) & file == 'end_game1'"`


- ***query.py***  
Run SQL queries on the NLP DataFrame and output to a `queries_dir` as a TSV. This uses a list of queries in `configs/queries.yml` to run many in one go, each saved to a filename key.


- ***screenplays.py***  
Convert the text into cleaned and formatted screenplay files. There are three types of output formats I've created. Specify the version as an external argument. If none are specified, version 3 is chosen.  <br><br>
Note: these are a mess of code. If someone has a better idea for how to best improve readability for both the script and the output, I'm all ears.)

  - `python screenplays.py 1`: Lines are formatted like 'The Cursed Child.' Optional paths are indented four spaces.
  ```
    He squints, frowns, then groans again, turning over onto his stomach.

    AMICUS
      "What the hell?"

    I clear my throat and swallow, trying not to show how nervous I am.

    MARCO
      "Yeah, what the hell. You tazed me again."

    AMICUS
      "What?"

    Amicus turns his head to look at me again, then looks away, letting out another groan.

    AMICUS
      "Ohh, my stomach. What did you do?"

    MARCO
      "Exactly what you did to me."
  ```

  - `python screenplays.py 2`: Alternative formatting with justify applied (using `textwrap`). Optional paths are indented four spaces.
  ```
    He squints, frowns, then groans again, turning over onto his stomach.

        AMICUS: "What the hell?"

    I clear my throat and swallow, trying not to show how nervous I am.

        MARCO: "Yeah, what the hell. You tazed me again."

        AMICUS: "What?"

    Amicus turns his head to look at me again, then looks away, letting out another
    groan.

        AMICUS: "Ohh, my stomach. What did you do?"

        MARCO: "Exactly what you did to me."
  ```

  - `python screenplays.py 3`: Lines are formatted like a screenplay. Speaker dialogue is centered. Text is still justified. Optional paths are marked explicitly with a line break and '[BRANCH]'.
  ```
    He squints, frowns, then groans again, turning over onto his stomach.

                                AMICUS
                 "What the hell?"

    I clear my throat and swallow, trying not to show how nervous I am.

                                MARCO
                 "Yeah, what the hell. You tazed me again."

                                AMICUS
                 "What?"

    Amicus turns his head to look at me again, then looks away, letting out
    another groan.

                                AMICUS
                 "Ohh, my stomach. What did you do?"

                                MARCO
                 "Exactly what you did to me."
  ```



- ***wordclouds.py***  
Create and save wordcloud images based on the text and mapped to a specific image. These can be populated by words from a specific filter of the data (e.g. only text from a specific file, only text spoken by Amicus, etc). This uses a list of wordclouds in `configs/wordclouds.yml` to create many in one go, with chosen filters. These can be customized to target only specific scenes, if you know the file and line numbers.  <br><br>
By default, a customized TF-IDF algorithm on content (non-stop) words is used to generate the wordclouds. I will not claim this has been coded correctly, but the wordclouds look nice, so I'm keeping it as is.  <br><br>
(Note: these all use black backgrounds at the moment. I haven't codifying user-supplied background colors yet. If you want to change them to another color, please do so in `wordclouds.py`.)  <br><br>
(See `examples/wordclouds` for a preselected list of generated clouds.)

  ```
  # Create a wordcloud of text spoken by Amicus.
  - filter: "speaker == 'amicus'"
    images:
      - sprites/amicus/amicus.png
  ```
  ```
  # Create wordclouds of text spoken by Cassius and Alexios.
  - filter: "speaker.isin(['cassius', 'alexios'])"
    images:
      - illustrations/poisoned.png
      - illustrations/alexandcassiuskiss.PNG
  ```
  ```
  # Create wordclouds of text spoken by Amicus or Marco in the endgame.
  - filter: "file == 'end_game1' & speaker.isin(['amicus', 'marco'])"
    images:
      - illustrations/farewell1.png
      - illustrations/wemadeit1.PNG
  ```


- ***analytics.py***  
Create custom Seaborn relplots of the data, designed via SQL queries on the datasets.  This uses a list of datasets and graphs in 'configs/analytics.yml' to create many in one go. Reference `adastra` and `adastra_nlp` in the SQL queries to call the relevant datasets.  <br><br>
(See `examples/analytics` for a preselected list of generated graphs.)
  ```
  # Define a custom dataset of characters to filter on, as well as the colors to display them with.
  datasets:
    characters:
      columns: [speaker, color]
      data: &characters_palette
        alexios : '#65ca68'
        amicus  : '#ff3333'
        cassius : '#FFFFFF'
        cato    : '#7a7a7a'
        marco   : '#0000FF'
        neferu  : '#ffcc00'
        virginia: '#8e389c'
  ```
  ```
  # Graph the number of lines spoken by character per file, and save to `{analytics_dir}/lines_per_character.png`.
  graphs:
    lines_per_character:
      sql: >
          select
              file,
              speaker,
              count(*) as num_lines
          from adastra
          inner join characters using(speaker)
          group by 1, 2
          order by 1, 2
      graph_args:
        x: file
        y: num_lines
        hue: speaker
        kind: line
        palette: *characters_palette
  ```
  ```
  # Graph the rolling sentiment of each character in the end-game, and save to `{analytics_dir}/sentiment/end_game1.png`.
  graphs:
    sentiment/end_game1:
      sql: >
          select
              line_idx,
              speaker,
              avg(sentiment) over (
                  partition by speaker
                  order by line_idx
                  rows between 9 preceding and current row
              ) as rolling_sentiment
          from adastra_nlp
              inner join characters using(speaker)
          where file = 'end_game1'
      axhline: 0.0
      remove_outliers: True
      graph_args:
        x: line_idx
        y: rolling_sentiment
        hue: speaker
        kind: line
        palette: *characters_palette
  ```



### Conclusion

This documentation is incomplete, but it's more than enough to get started! I'll continue to document and expand the project in the coming weeks. I've had a lot of fun building out this project, and I hope that someone else gets use out of all this work. Regardless, enjoy the wordclouds and a way to collect screenplay files! Please reach out to `u/OrigamiOtter` for questions and feedback!
