# stdlib
import keyword
import pathlib
import re
import token
import tokenize
from collections import Counter

# 3rd party
from wordcloud import WordCloud
import pygit2

# this package
from parsers import PythonParser, CParser, CppParser, GenericParser

# git_path = '/home/domdf/GunShotMatch/GunShotMatch/GuiV2'
git_path = 'C:/Users/dom13/GunShotMatch/GunShotMatch/GuiV2'

ignore_keywords = True


def create_word_cloud(word_counts, ignore_keywords=False):
	# maskArray = numpy.array(Image.open("cloud.png"))
	if ignore_keywords:
		
		cloud = WordCloud(
				width=1920,
				height=1080,
				background_color="white",
				max_words=len(word_counts),
				# mask=maskArray,
				stopwords=set(keyword.kwlist),
				)
	else:
		cloud = WordCloud(
				width=1920,
				height=1080,
				background_color="white",
				max_words=len(word_counts),
				# mask=maskArray,
				)
		
	cloud.generate_from_frequencies(word_counts)
	cloud.to_file("wordCloud.png")


# def remove_comments(fname):
# 	"""
# 	Strip comments and docstrings from a file.
#
# 	From https://stackoverflow.com/a/1769577
#
# 	:param fname:
# 	:type fname:
# 	:return:
# 	:rtype:
# 	"""
#
# 	source = open(fname)
#
# 	output = ''
#
# 	prev_toktype = token.INDENT
# 	first_line = None
# 	last_lineno = -1
# 	last_col = 0
#
# 	tokgen = tokenize.generate_tokens(source.readline)
# 	for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
# 		if 0:   # Change to if 1 to see the tokens fly by.
# 			print("%10s %-14s %-20r %r" % (
# 				tokenize.tok_name.get(toktype, toktype),
# 				"%d.%d-%d.%d" % (slineno, scol, elineno, ecol),
# 				ttext, ltext
# 				))
# 		if slineno > last_lineno:
# 			last_col = 0
# 		if scol > last_col:
# 			output += " " * (scol - last_col)
# 		if toktype == token.STRING and prev_toktype == token.INDENT:
# 			# Docstring
# 			output += "#--"
# 		elif toktype == tokenize.COMMENT:
# 			# Comment
# 			output += "##\n"
# 		else:
# 			output += ttext
# 		prev_toktype = toktype
# 		last_col = ecol
# 		last_lineno = elineno
#
# 	return output


word_counts = dict()

ignore_dirs = [
		git_path + "/CalibreSearch",
		]



def wordcloud_from_directory(directory, ignore_dirs=None):
	pyparser = PythonParser()
	cparser = CParser()
	cppparser = CppParser()
	genparser = GenericParser()
	
	for path in pathlib.Path(directory).rglob('*.py'):
		print(path)
		if ignore_dirs:
			for dir in ignore_dirs:
				if str(path).startswith(dir):
					continue
		
		if path.suffix in {".py"}:
			words = pyparser.parse_file(path)
		elif path.suffix in {".c, .h"}:
			words = pyparser.parse_file(path)
		# TODO: Disinguish c header from cpp header
		elif path.suffix in {".cpp, .h"}:
			words = pyparser.parse_file(path)
		else:
			words = genparser.parse_file(path)
			
		for word, count in Counter(words).items():
			if word in word_counts:
				word_counts[word] += count
			else:
				word_counts[word] = count

	create_word_cloud(word_counts, True)

def wordcloud_from_git(url, ignore_dirs=None):
	
	output_path = pathlib.Path(".").resolve() / "git"
	
	if output_path.exists():
		output_path.unlink()
	
	pygit2.clone_repository(url,str(output_path))
	
	wordcloud_from_directory(str(output_path), ignore_dirs)

	if output_path.exists():
		output_path.unlink()

print(word_counts)

# wordcloud_from_directory(git_path, ignore_dirs)
wordcloud_from_git("https://github.com/python-visualization/folium")

