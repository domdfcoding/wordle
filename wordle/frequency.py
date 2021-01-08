#!/usr/bin/env python
#
#  frequency.py
"""
Functions to determine word token frequency for wordclouds.

.. versionadded:: 0.2.0
"""
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import pathlib
import re
import tempfile
import typing
from collections import Counter
from string import punctuation
from typing import Optional, Sequence

# 3rd party
import pygments.lexers  # type: ignore
import pygments.token  # type: ignore
import pygments.util  # type: ignore
from domdf_python_tools.typing import PathLike

# this package
from wordle.utils import clone_into_tmpdir

__all__ = ["frequency_from_directory", "frequency_from_file", "frequency_from_git", "get_tokens"]


def get_tokens(filename: PathLike) -> typing.Counter[str]:
	"""
	Returns a :class:`collections.Counter` of the tokens in a file.

	:param filename: The file to parse.

	:return: A count of words etc. in the file.
	"""

	total: typing.Counter[str] = Counter()

	if not isinstance(filename, pathlib.Path):
		filename = pathlib.Path(filename)

	try:
		lex = pygments.lexers.get_lexer_for_filename(filename)
	except pygments.util.ClassNotFound:
		return total

	for token in lex.get_tokens(filename.read_text()):
		if token[0] in pygments.token.Comment:
			continue

		if token[0] in pygments.token.Text:
			if token[1] == '\n':
				continue
			if token[1] == ' ':
				continue
			if re.match(r"^\t*$", token[1]):
				continue
			if re.match(r"^\s*$", token[1]):
				continue

		if token[0] in pygments.token.String:
			if token[1] == '"':
				continue

			if token[0] in pygments.token.String.Escape:
				if re.match(r"\\*", token[1]):
					continue

		if token[0] in pygments.token.String.Double:
			if token[1] in '\n':
				continue
			if re.match(r'^"*$', token[1]):
				continue

		if token[0] in pygments.token.String.Single:
			if token[1] in '\n':
				continue
			if re.match(r"^'*$", token[1]):
				continue

		if token[0] in pygments.token.Punctuation and token[1] in "[],{}:();":
			continue

		if token[0] in pygments.token.Operator:
			continue

		if token[0] in pygments.token.String.Affix:
			continue

		if token[0] in pygments.token.String.Interpol and token[1] in "{}":
			continue

		if re.match("^:*$", token[1]):
			continue

		total += Counter(re.split("[ \n\t]", token[1]))

	punctuation_to_delete = ['', ' ']

	for word in total:
		if re.match(f"^[{punctuation}]+$", word):
			punctuation_to_delete.append(word)

	for word in punctuation_to_delete:
		del total[word]

	all_words: typing.Counter[str] = Counter()

	for word in total:
		if word.endswith(':'):
			all_words[word.rstrip(':')] = total[word]
		else:
			all_words[word] = total[word]

	return all_words


def frequency_from_file(
		filename: PathLike,
		exclude_words: Sequence[str] = (),
		) -> Counter:
	"""
	Returns a dictionary mapping the words in the file to their frequencies.

	:param filename: The file to process
	:param exclude_words: An optional list of words to exclude

	.. versionadded:: 0.2.0

	.. seealso:: func:`~.get_tokens`
	"""

	word_counts = get_tokens(filename)

	for word in exclude_words:
		if word in word_counts:
			del word_counts[word]

	return word_counts


def frequency_from_directory(
		directory: PathLike,
		exclude_words: Sequence[str] = (),
		exclude_dirs: Sequence[PathLike] = (),
		) -> Counter:
	"""
	Returns a dictionary mapping the words in files in ``directory`` to their frequencies.

	:param directory: The directory to process
	:param exclude_words: An optional list of words to exclude
	:param exclude_dirs: An optional list of directories to exclude.

	.. versionadded:: 0.2.0
	"""

	# TODO: only certain file extensions

	directory = pathlib.Path(directory).absolute()

	exclude_dirs_list = [".git"]

	for d in exclude_dirs:
		d = pathlib.Path(d)

		if d.is_absolute():
			d = d.relative_to(directory)

		exclude_dirs_list.append(str(d))

	def is_excluded(path):
		for dir_name in exclude_dirs_list:
			if re.match(dir_name, path.relative_to(directory).as_posix()):
				return True
		return False

	word_counts: typing.Counter[str] = Counter()

	for file in directory.rglob("**/*.*"):
		if file.is_file() and not is_excluded(file):
			word_counts += get_tokens(file)

	for word in exclude_words:
		if word in word_counts:
			del word_counts[word]

	return word_counts


def frequency_from_git(
		git_url: str,
		sha: Optional[str] = None,
		depth: Optional[int] = None,
		exclude_words: Sequence[str] = (),
		exclude_dirs: Sequence[PathLike] = (),
		) -> Counter:
	"""
	Returns a dictionary mapping the words in files in ``directory`` to their frequencies.

	:param git_url: The url of the git repository to process
	:param sha: An optional SHA hash of a commit to checkout.
	:param depth: An optional depth to clone at. If :py:obj:`None` and ``sha`` is :py:obj:`None` the depth is ``1``.
		If :py:obj:`None` and ``sha`` is given the depth is unlimited.
	:param exclude_words: An optional list of words to exclude.
	:param exclude_dirs: An optional list of directories to exclude.

	.. versionadded:: 0.2.0
	"""

	with tempfile.TemporaryDirectory() as tmpdir:
		clone_into_tmpdir(git_url, tmpdir, sha=sha, depth=depth)

		return frequency_from_directory(
				tmpdir,
				exclude_dirs=exclude_dirs,
				exclude_words=exclude_words,
				)
