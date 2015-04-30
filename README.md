This is a simple python script for searching for files with equivalent contents, but possibly different names.

It is very much a work in progress.

usage: duplicates.py [-h] [-o [OUTPUT_FILENAME]] [-v] [-L]
                     input_dirs [input_dirs ...]

Searches directory and its subdirectories for files with duplicate contents,
optionally writing out duplicates to either a text file or stdout

positional arguments:
  input_dirs            Input directories to be search, separated by
                        whitespace. Note that subdirectories are searched

optional arguments:
  -h, --help            show this help message and exit
  -o [OUTPUT_FILENAME], --output [OUTPUT_FILENAME]
                        optional output text file
  -v, --verbose         Increase verbosity
  -L, --no-follow-links
                        Don't follow symlinks
