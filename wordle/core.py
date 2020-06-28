#!/usr/bin/env python
#
#  core.py
"""
Core functionality.
"""
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#  Based on "wordcloud" by Andreas Christian Mueller and Paul Nechifor.
#  Copyright (c) 2012
#  License: MIT
#

# stdlib
import os
import pathlib
import re
import tempfile
from collections import Counter
from string import punctuation
from typing import Callable, Optional, Sequence, Union
import typing

# 3rd party
import numpy  # type: ignore
import pygments.lexers  # type: ignore
import pygments.token  # type: ignore
import pygments.util  # type: ignore
from dulwich import porcelain  # type: ignore
from wordcloud import WordCloud  # type: ignore


__all__ = ["Wordle", "export_wordcloud", "get_tokens"]


PathLike = Union[str, pathlib.Path, os.PathLike]


class Wordle(WordCloud):
	r"""
	Generate word clouds from source code.

	:param font_path: Font path to the font that will be used (OTF or TTF).
		Defaults to DroidSansMono path on a Linux machine. If you are on
		another OS or don't have this font, you need to adjust this path.
	:type width: int, optional

	:param width: The width of the canvas. Default ``400``
	:type width: int, optional

	:param height: The height of the canvas. Default 200
	:type height: int, optional

	:param prefer_horizontal: The ratio of times to try horizontal fitting as opposed to vertical.
		If prefer_horizontal < 1, the algorithm will try rotating the word
		if it doesn't fit. (There is currently no built-in way to get only
		vertical words.) Default ``0.90``
	:type prefer_horizontal: float

	:param mask: If not ``None``, gives a binary mask on where to draw words. If mask is not
		``None``, width and height will be ignored and the shape of mask will be
		used instead. All white (``#FF`` or ``#FFFFFF``) entries will be considerd
		"masked out" while other entries will be free to draw on. Default ``None``
	:type mask: nd-array or None

	:param contour_width: If mask is not ``None`` and contour_width > 0, draw the mask contour. Default ``0``
	:type contour_width: float

	:param contour_color: Mask contour color. Default ``"black"``
	:type contour_color: str

	:param scale: Scaling between computation and drawing. For large word-cloud images,
		using scale instead of larger canvas size is significantly faster, but
		might lead to a coarser fit for the words. Default ``1``
	:type scale: float

	:param min_font_size: Smallest font size to use. Will stop when there is no more room in this
		size. Default ``4``
	:type min_font_size: int

	:param font_step: Step size for the font. font_step > 1 might speed up computation but
		give a worse fit. Default ``1``
	:type font_step: int

	:param max_words: The maximum number of words. Default 200
	:type max_words: int

	:param background_color: Background color for the word cloud image. Default ``"black"``
	:type background_color: str

	:param max_font_size: Maximum font size for the largest word. If None, height of the image is
		used. Default ``None``

	:param mode: Transparent background will be generated when mode is "RGBA" and
		background_color is None. Default ``"RGB"``
	:type mode: str

	:param relative_scaling: Importance of relative word frequencies for font-size.  With
		relative_scaling=0, only word-ranks are considered.  With
		relative_scaling=1, a word that is twice as frequent will have twice
		the size.  If you want to consider the word frequencies and not only
		their rank, relative_scaling around .5 often looks good.
		If 'auto' it will be set to 0.5 unless repeat is true, in which
		case it will be set to 0. Default ``"auto"``
	:type relative_scaling: float

	:param color_func: Callable with parameters word, font_size, position, orientation,
		font_path, random_state that returns a PIL color for each word.
		Overwrites "colormap".
		See colormap for specifying a matplotlib colormap instead.
		To create a word cloud with a single color, use
		``color_func=lambda *args, **kwargs: "white"``.
		The single color can also be specified using RGB code. For example
		``color_func=lambda *args, **kwargs: (255,0,0)`` sets color to red.

	:param regexp: Regular expression to split the input text into tokens in process_text.
		If None is specified, ``r"\w[\w']+"`` is used. Ignored if using
		generate_from_frequencies.
	:type regexp: str, optional

	:param collocations: Whether to include collocations (bigrams) of two words. Ignored if using
		generate_from_frequencies. Default ``True``
	:type collocations: bool, optional

	:param colormap: Matplotlib colormap to randomly draw colors from for each word.
		Ignored if "color_func" is specified.
	:type colormap: string or matplotlib colormap, default="viridis"

	:param repeat: Whether to repeat words and phrases until max_words or min_font_size
		is reached. Default ``False``
	:type repeat: bool

	:param include_numbers: Whether to include numbers as phrases or not. Default ``False``
	:type include_numbers: bool

	:param min_word_length: Minimum number of letters a word must have to be included. Default ``0``
	:type min_word_length: int

	:param random_state: Seed for the randomness that determines the colour and position of words.
	:type random_state int:

	.. note:

		Larger canvases with make the code significantly slower. If you need a
		large word cloud, try a lower canvas size, and set the scale parameter.
		The algorithm might give more weight to the ranking of the words
		than their actual frequencies, depending on the ``max_font_size`` and the
		scaling heuristic.

	"""

	def to_html(self):
		raise NotImplementedError

	def __init__(
			self,
			font_path: Optional[str] = None,
			width: int = 400,  # 1920
			height: int = 200,  # 1080
			prefer_horizontal: float = 0.90,
			mask: Optional[numpy.ndarray] = None,
			contour_width: float = 0,
			contour_color: str = "black",
			scale: float = 1,
			min_font_size: int = 4,
			font_step: int = 1,
			max_words: int = 200,
			background_color: str = "black",
			max_font_size: Optional[int] = None,
			mode: str = "RGB",
			relative_scaling: Union[str, float] = "auto",
			color_func: Optional[Callable] = None,
			regexp: Optional[str] = None,
			collocations: bool = True,
			colormap=None,
			repeat: bool = False,
			include_numbers: bool = False,
			min_word_length: int = 0,
			# margin=2,
			# ranks_only=None,
			random_state=None,
			) -> None:

		super().__init__(
				font_path=font_path,
				width=width,
				height=height,
				prefer_horizontal=prefer_horizontal,
				mask=mask,
				contour_width=contour_width,
				contour_color=contour_color,
				scale=scale,
				min_font_size=min_font_size,
				font_step=font_step,
				max_words=max_words,
				background_color=background_color,
				max_font_size=max_font_size,
				mode=mode,
				relative_scaling=relative_scaling,
				color_func=color_func,
				regexp=regexp,
				collocations=collocations,
				colormap=colormap,
				repeat=repeat,
				include_numbers=include_numbers,
				min_word_length=min_word_length,
				# margin=margin,
				# ranks_only=ranks_only,
				random_state=random_state,
				)

	def generate_from_file(
			self,
			filename: Union[str, pathlib.Path, os.PathLike],
			outfile: Optional[Union[str, pathlib.Path, os.PathLike]] = None,
			exclude_words: Optional[Sequence[str]] = None,
			max_font_size: Optional[int] = None
			) -> "Wordle":
		"""
		Create a word_cloud from a source code file.

		:param filename: The file to process
		:param outfile: The file to save the wordle as. Supported formats are ``PNG``, ``JPEG`` and SVG.
		If ``None`` the wordle is not saved
		:param exclude_words: An optional list of words to exclude
		:param max_font_size: Use this font-size instead of self.max_font_size
		:type max_font_size: int
		"""

		word_counts = get_tokens(filename)
		if exclude_words is None:
			exclude_words = []

		for word in exclude_words:
			if word in word_counts:
				del word_counts[word]

		self.generate_from_frequencies(word_counts, max_font_size=max_font_size)

		if outfile:
			export_wordcloud(self, outfile)

		return self

	def generate_from_directory(
			self,
			directory: PathLike,
			outfile: Optional[PathLike] = None,
			exclude_words: Optional[Sequence[str]] = None,
			exclude_dirs: Optional[Sequence[PathLike]] = None,
			max_font_size: Optional[int] = None
			) -> "Wordle":
		"""
		Create a word_cloud from a directory of source code files.

		:param directory: The directory to process
		:param outfile: The file to save the wordle as. Supported formats are ``PNG``, ``JPEG`` and SVG.
		If ``None`` the wordle is not saved
		:param exclude_words: An optional list of words to exclude
		:param exclude_dirs: An optional list of directories to exclude
		:param max_font_size: Use this font-size instead of self.max_font_size
		:type max_font_size: int
		"""

		# TODO: only certain file extensions

		directory = pathlib.Path(directory).absolute()

		if exclude_dirs:
			exclude_dirs = [pathlib.Path(d).relative_to(directory) for d in exclude_dirs]
		else:
			exclude_dirs = []

		if exclude_words is None:
			exclude_words = []

		def is_excluded(path):
			for dir_name in exclude_dirs:
				if dir_name in path.stem:
					return True
			return False

		word_counts: typing.Counter[str] = Counter()

		for file in directory.rglob("**/*.*"):
			if file.is_file() and not is_excluded(file):
				word_counts += get_tokens(file)

		for word in exclude_words:
			if word in word_counts:
				del word_counts[word]

		self.generate_from_frequencies(word_counts, max_font_size=max_font_size)

		if outfile is not None:
			export_wordcloud(self, outfile)

		# with open("wordcount.json", "w") as fp:
		# 	json.dump(word_counts, fp)

		return self

	def generate_from_git(
			self,
			git_url: str,
			outfile: Optional[PathLike] = None,
			exclude_words: Optional[Sequence[str]] = None,
			exclude_dirs: Optional[Sequence[PathLike]] = None,
			max_font_size: Optional[int] = None
			) -> "Wordle":
		"""
		Create a word_cloud from a directory of source code files.

		:param git_url: The url of the git repository to process
		:param outfile: The file to save the wordle as. Supported formats are ``PNG``, ``JPEG`` and SVG.
		If ``None`` the wordle is not saved
		:param exclude_words: An optional list of words to exclude
		:param exclude_dirs: An optional list of directories to exclude
		:param max_font_size: Use this font-size instead of self.max_font_size
		:type max_font_size: int
		"""

		# TODO: only certain file extensions

		with tempfile.TemporaryDirectory() as tmpdir:
			directory = pathlib.Path(tmpdir)
			porcelain.clone(git_url, target=str(directory), depth=1)

			self.generate_from_directory(
					tmpdir,
					outfile=outfile,
					exclude_dirs=exclude_dirs,
					exclude_words=exclude_words,
					max_font_size=max_font_size,
					)

		return self


def export_wordcloud(word_cloud: WordCloud, outfile: PathLike) -> None:
	"""
	Export a wordcloud to a file.

	:param word_cloud:
	:param outfile: The file to export the wordcloud to
	"""

	outfile = pathlib.Path(outfile)

	if outfile.suffix == ".svg":
		outfile.write_text(word_cloud.to_svg())
	else:
		word_cloud.to_file(str(outfile))


def get_tokens(filename: PathLike) -> typing.Counter[str]:
	"""

	:param filename: The file to parse

	:return: A count of words etc. in the file
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
			if token[1] in "\n":
				continue
			if re.match(r'^"*$', token[1]):
				continue

		if token[0] in pygments.token.String.Single:
			if token[1] in "\n":
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

		total += Counter(token[1].split(' '))

	if '' in total:
		del total['']

	for char in punctuation:
		if char in total:
			del total[char]

	all_words: typing.Counter[str] = Counter()

	for word in total:
		if word.endswith(':'):
			all_words[word.rstrip(':')] = total[word]
		else:
			all_words[word] = total[word]

	return all_words
