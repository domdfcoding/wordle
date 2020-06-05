# stdlib
import keyword
import pathlib
import re
import token
import tokenize
from collections import Counter

from .base import BaseParser

class PythonParser(BaseParser):
	def __init__(
			self,
			exclude_keywords=True,
			exclude_list=None,
			ignore_comments=True,
			ignore_docstrings=True,
			debug=False,
			):
		
		self.exclude_keywords = exclude_keywords
		self.exclude_list = exclude_list
		self.ignore_comments = ignore_comments
		self.ignore_docstrings = ignore_docstrings
		self.debug = debug
		
		self.kwlist = keyword.kwlist
	
	def parse_file(self, filename):

		# First Strip comments and docstrings from a file
		# From https://stackoverflow.com/a/1769577
		
		source = open(filename, encoding="utf-8")
		
		output = ''
		
		prev_toktype = token.INDENT
		first_line = None
		last_lineno = -1
		last_col = 0
		
		tokgen = tokenize.generate_tokens(source.readline)
		for toktype, ttext, (slineno, scol), (elineno, ecol), ltext in tokgen:
			if self.debug:  # Change to if 1 to see the tokens fly by.
				print("%10s %-14s %-20r %r" % (
						tokenize.tok_name.get(toktype, toktype),
						"%d.%d-%d.%d" % (slineno, scol, elineno, ecol),
						ttext, ltext
						))
			
			if slineno > last_lineno:
				last_col = 0
			if scol > last_col:
				output += " " * (scol - last_col)
			
			if self.ignore_docstrings and toktype == token.STRING and prev_toktype == token.INDENT:
				# Docstring
				output += "#--"
			elif self.ignore_comments and toktype == tokenize.COMMENT:
				# Comment
				output += "##\n"
			else:
				output += ttext
				
			prev_toktype = toktype
			last_col = ecol
			last_lineno = elineno
		
		counts = self.count_words(output)
		
		if self.exclude_keywords:
			counts = self.exclude_words(counts, self.kwlist)
		
		if self.exclude_list:
			counts = self.exclude_words(counts, self.exclude_list)
		
		# return the counts
		return counts
