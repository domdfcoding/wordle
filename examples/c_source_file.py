"""
Create a wordcloud from a single C source file
"""

from wordle.core import export_wordcloud, Wordle

w = Wordle()
w.generate_from_file("example.c", outfile="c_wordcloud.svg")
export_wordcloud(w, outfile="c_wordcloud.png")
