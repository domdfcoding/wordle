# stdlib
import keyword
import pathlib
import re
import token
import tokenize
from collections import Counter


class BaseParser:
	
	@staticmethod
	def count_words(text):
		# Find all words
		words = re.findall(r"[\w']+", text)
		
		# Count words
		counts = Counter(words)
		
		return counts
	
	@staticmethod
	def exclude_words(counts, exclude_list):
		# Remove keywords
		for kword in exclude_list:
			if kword in counts:
				del counts[kword]
		
		return counts