"""
Create a wordcloud from the Folium git repository.

https://github.com/python-visualization/folium
"""

from wordle.core import export_wordcloud, Wordle

w = Wordle()
w.generate_from_git("https://github.com/python-visualization/folium", outfile="folium_wordcloud.svg")
export_wordcloud(w, outfile="folium_wordcloud.png")
