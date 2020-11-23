"""
Create a wordcloud from the Folium git repository.

https://github.com/python-visualization/folium
"""

# this package
from wordle import Wordle, export_wordcloud

w = Wordle(random_state=5678)
w.generate_from_git("https://github.com/python-visualization/folium", outfile="folium_wordcloud.svg")
export_wordcloud(w, outfile="folium_wordcloud.png")
