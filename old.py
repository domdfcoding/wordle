# stdlib
import keyword

# git_path = '/home/domdf/GunShotMatch/GunShotMatch/GuiV2'
git_path = 'C:/Users/dom13/GunShotMatch/GunShotMatch/GuiV2'

ignore_keywords = True

#
# width=1920,
# height=1080,
# background_color="white",
# stopwords=set(keyword.kwlist),
#
# cloud.generate_from_frequencies(word_counts)
# cloud.to_file("wordCloud.png")

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

py_kwlist = keyword.kwlist

c_kwlist = [
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


def blotOutNonNewlines(strIn):  # Return a string containing only the newline chars contained in strIn
	return "" + ("\n" * strIn.count('\n'))


def replacer(match):
	s = match.group(0)
	if s.startswith('/'):  # Matched string is //...EOL or /*...*/  ==> Blot out all non-newline chars
		return blotOutNonNewlines(s)
	else:  # Matched string is '...' or "..."  ==> Keep unchanged
		return s


#
# pattern = re.compile(
# 		r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
# 		re.DOTALL | re.MULTILINE
# 		)

cpp_kwlist = [
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
