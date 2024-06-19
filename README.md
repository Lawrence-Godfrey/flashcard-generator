# Flashcard Generator

Flashcard Generator is a Python command-line program that generates flashcards
given a file or directory of markdown files. The program will search recursively
through the directory and generate a corresponding markdown file of flashcards based
on the contents. The flashcards are generated using the GPT-4-Turbo model from OpenAI.

## Installation

This can be installed as a command-line program using:


```bash
pip install .
```

## Usage

To see all possible options, you can run:

```bash
generate_flashcards --help
```

To generate flashcards from a directory of markdown files, run:

```bash
generate_flashcards -a api_key --model="gpt-4-turbo" --verbose --input_dir="/path/to/input/dir/" process_files
```

This will generate a new `flashcards` directory in the input directory.