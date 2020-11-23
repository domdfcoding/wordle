"""
Create a wordcloud from a single C source file
"""

# this package
from wordle import Wordle, export_wordcloud

w = Wordle(random_state=5678)
w.generate_from_file("example.c", outfile="c_wordcloud.svg")
export_wordcloud(w, outfile="c_wordcloud.png")
