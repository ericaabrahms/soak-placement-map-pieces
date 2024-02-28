# Placement Map Pieces

This will generate map pieces from a .csv file with the relevant camp data modeled after Camp Pieces *2024

## File setup
Export the relevant sheet from google sheets as a .csv file and save to this project.
The file path is set in `datastore.py` in the `read_csv` function. As of Feb 27, 2024 it is set to read `placement-temp.csv`

## To Run
From the root of the project:

Run `python3 main.py`  to generate all images

An optional argument to generate images for camps with names that include that argument. e.g.

`python3 main.py fire`

will generate image for Fire Camp and Fire Safety Support Camp

Use quotes if the camp name contains spaces. e.g.

`python3 main.py 'black rock observatory'`

Camps that are too small (< 20' in either dimension) are too small to be automatically generated in any reasonable fashion.
A warning with the camp name will be printed in the terminal when the script encounters one of these

Images are saved to the 'images' directory.

## Install

```
brew install pipx    # or your package manager equivalent
pipx ensurepath      # ensure it's using the right files
pipx install poetry  # install our *actual* package installer
poetry install       # install the dependencies for this project
```

## Risky Choices
- The camp names are mapped to a column with no heading.
- Property names are derived from column headings.  There are duplicates of these in the csv.  The last column trumps (e.g. If Col A and Col Z are named 'Coffee', the data from Col Z will be used.)
