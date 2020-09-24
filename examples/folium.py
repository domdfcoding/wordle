"""
Create a wordcloud from the Folium git repository.

https://github.com/python-visualization/folium
"""

# this package
from wordle.core import Wordle, export_wordcloud

w = Wordle()
w.generate_from_git("https://github.com/python-visualization/folium", outfile="folium_wordcloud.svg")
export_wordcloud(w, outfile="folium_wordcloud.png")
