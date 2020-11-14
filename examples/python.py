"""
Create a wordcloud from a single Python source file
"""

# stdlib
import pathlib

# this package
from wordle.core import Wordle, export_wordcloud

filename = pathlib.Path('.').absolute().parent / "wordle/core.py"

w = Wordle()
w.generate_from_file(filename, outfile="python_wordcloud.svg")
export_wordcloud(w, outfile="python_wordcloud.png")
