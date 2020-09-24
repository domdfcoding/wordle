"""
Create a wordcloud from a single C source file
"""

# this package
from wordle.core import Wordle, export_wordcloud

w = Wordle()
w.generate_from_file("example.c", outfile="c_wordcloud.svg")
export_wordcloud(w, outfile="c_wordcloud.png")
