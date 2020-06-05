# stdlib
import keyword
import pathlib
import re
import token
import tokenize
from collections import Counter

from .base import BaseParser


class CParser(BaseParser):
	def __init__(
			self,
			exclude_keywords=True,
			exclude_list=None,
			ignore_comments=True,
			debug=False,
			):
		
		self.exclude_keywords = exclude_keywords
		self.exclude_list = exclude_list
		self.ignore_comments = ignore_comments
		self.debug = debug
		
		self.kwlist = [
				"auto",
				"break",
				"case",
				"char",
				"const",
				"continue",
				"default",
				"do",
				"double",
				"else",
				"enum",
				"extern",
				"float",
				"for",
				"goto",
				"if",
				"int",
				"long",
				"register",
				"return",
				"short",
				"signed",
				"sizeof",
				"static",
				"struct",
				"switch",
				"typedef",
				"union",
				"unsigned",
				"void",
				"volatile",
				"while",
				]
	
	def parse_file(self, filename):
		
		source = open(filename, encoding="utf-8")
		text = source.read()
		
		def blotOutNonNewlines(strIn):  # Return a string containing only the newline chars contained in strIn
			return "" + ("\n" * strIn.count('\n'))
		
		def replacer(match):
			s = match.group(0)
			if s.startswith('/'):  # Matched string is //...EOL or /*...*/  ==> Blot out all non-newline chars
				return blotOutNonNewlines(s)
			else:  # Matched string is '...' or "..."  ==> Keep unchanged
				return s
		
		pattern = re.compile(
				r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
				re.DOTALL | re.MULTILINE
				)
		
		output = re.sub(pattern, replacer, text)
		
		counts = self.count_words(output)
		
		if self.exclude_keywords:
			counts = self.exclude_words(counts, self.kwlist)
		
		if self.exclude_list:
			counts = self.exclude_words(counts, self.exclude_list)
		
		# return the counts
		return counts


class CppParser(CParser):
	def __init__(
			self,
			exclude_keywords=True,
			exclude_list=None,
			ignore_comments=True,
			debug=False,
			):
		
		self.exclude_keywords = exclude_keywords
		self.exclude_list = exclude_list
		self.ignore_comments = ignore_comments
		self.debug = debug
		
		self.kwlist = [
					"alignas",
					"alignof",
					"and",
					"and_eq",
					"asm",
					"atomic_cancel",
					"atomic_commit",
					"atomic_noexcept",
					"auto",
					"bitand",
					"bitor",
					"bool",
					"break",
					"case",
					"catch",
					"char",
					"char8_t",
					"char16_t",
					"char32_t",
					"class",
					"compl",
					"concept",
					"const",
					"consteval",
					"constexpr",
					"constinit",
					"const_cast",
					"continue",
					"co_await",
					"co_return",
					"co_yield",
					"decltype",
					"default",
					"delete",
					"do",
					"double",
					"dynamic_cast",
					"else",
					"enum",
					"explicit",
					"export",
					"extern",
					"false",
					"float",
					"for",
					"friend",
					"goto",
					"if",
					"inline",
					"int",
					"long",
					"mutable",
					"namespace",
					"new",
					"noexcept",
					"not",
					"not_eq",
					"nullptr",
					"operator",
					"or",
					"or_eq",
					"private",
					"protected",
					"public",
					"reflexpr",
					"register",
					"reinterpret_cast",
					"requires",
					"return",
					"short",
					"signed",
					"sizeof",
					"static",
					"static_assert",
					"static_cast",
					"struct",
					"switch",
					"synchronized",
					"template",
					"this",
					"thread_local",
					"throw",
					"true",
					"try",
					"typedef",
					"typeid",
					"typename",
					"union",
					"unsigned",
					"using",
					"virtual",
					"void",
					"volatile",
					"wchar_t",
					"while",
					"xor",
					"xor_eq",
				]
	


