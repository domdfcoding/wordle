from .python import PythonParser
from .c_cpp import CParser, CppParser
from .base import BaseParser


class GenericParser(BaseParser):
	def __init__(
			self,
			exclude_list=None,
			):
		
		self.exclude_list = exclude_list
	
	def parse_file(self, filename):
		
		source = open(filename, encoding="utf-8")
		text = source.read()
		counts = self.count_words(text)
		
		if self.exclude_list:
			counts = self.exclude_words(counts, self.exclude_list)
		
		# return the counts
		return counts
