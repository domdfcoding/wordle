#!/usr/bin/env python
#
#  __init__.py
"""
Create wordclouds from git repositories, directories and source files.
"""
#
#  Copyright (c) 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#  Based on "wordcloud" by Andreas Christian Mueller and Paul Nechifor.
#  Copyright (c) 2012
#  MIT Licensed
#

# stdlib
import os
import pathlib
import sys
import time
import typing
from typing import Callable, Optional, Sequence, Union

# 3rd party
import numpy
from domdf_python_tools.typing import PathLike
from matplotlib.colors import Colormap  # type: ignore
from numpy.random.mtrand import RandomState
from wordcloud import WordCloud  # type: ignore

# this package
from wordle.frequency import frequency_from_directory, frequency_from_file, get_tokens
from wordle.utils import _TemporaryDirectory, clone_into_tmpdir

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.2.1"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["Wordle", "export_wordcloud", "get_tokens"]


class Wordle(WordCloud):
	r"""
	Generate word clouds from source code.

	:param font_path: Font path to the font that will be used (OTF or TTF).
		Defaults to DroidSansMono path on a Linux machine. If you are on
		another OS or don't have this font, you need to adjust this path.

	:param width: The width of the canvas.
	:param height: The height of the canvas.

	:param prefer_horizontal: The ratio of times to try horizontal fitting as opposed to vertical.
		If prefer_horizontal < 1, the algorithm will try rotating the word
		if it doesn't fit. (There is currently no built-in way to get only vertical words.)

	:param mask: If not :py:obj:`None`, gives a binary mask on where to draw words. If mask is not
		:py:obj:`None`, width and height will be ignored and the shape of mask will be
		used instead. All white (``#FF`` or ``#FFFFFF``) entries will be considerd
		"masked out" while other entries will be free to draw on.

	:param contour_width: If mask is not :py:obj:`None` and contour_width > 0, draw the mask contour.
	:param contour_color: Mask contour color.

	:param scale: Scaling between computation and drawing. For large word-cloud images,
		using scale instead of larger canvas size is significantly faster, but
		might lead to a coarser fit for the words.

	:param min_font_size: Smallest font size to use.
		Will stop when there is no more room in this size.

	:param font_step: Step size for the font.
		``font_step`` > 1 might speed up computation but give a worse fit.

	:param max_words: The maximum number of words.
	:param background_color: Background color for the word cloud image.
	:param max_font_size: Maximum font size for the largest word.
		If :py:obj:`None` the height of the image is used.

	:param mode: Transparent background will be generated when mode is "RGBA" and
		background_color is None.

	:param relative_scaling: Importance of relative word frequencies for font-size.  With
		relative_scaling=0, only word-ranks are considered.  With
		relative_scaling=1, a word that is twice as frequent will have twice
		the size.  If you want to consider the word frequencies and not only
		their rank, relative_scaling around .5 often looks good.
		If 'auto' it will be set to 0.5 unless repeat is true, in which
		case it will be set to 0.

	:param color_func: Callable with parameters ``word``, ``font_size``, ``position``, ``orientation``,
		``font_path``, ``random_state`` which returns a PIL color for each word.
		Overwrites "colormap".
		See ``colormap`` for specifying a matplotlib colormap instead.
		To create a word cloud with a single color, use ``color_func=lambda *args, **kwargs: "white"``.
		The single color can also be specified using RGB code.
		For example ``color_func=lambda *args, **kwargs: (255,0,0)`` sets the color to red.

	:param regexp: Regular expression to split the input text into tokens in process_text.
		If None is specified, ``r"\w[\w']+"`` is used. Ignored if using
		generate_from_frequencies.

	:param collocations: Whether to include collocations (bigrams) of two words. Ignored if using
		generate_from_frequencies.

	:param colormap: Matplotlib colormap to randomly draw colors from for each word.
		Ignored if "color_func" is specified. Default "viridis".
	:no-default colormap:

	:param repeat: Whether to repeat words and phrases until max_words or min_font_size is reached.
	:param include_numbers: Whether to include numbers as phrases or not.
	:param min_word_length: Minimum number of letters a word must have to be included.
	:param random_state: Seed for the randomness that determines the colour and position of words.

	.. note::

		Larger canvases with make the code significantly slower. If you need a
		large word cloud, try a lower canvas size, and set the scale parameter.
		The algorithm might give more weight to the ranking of the words
		than their actual frequencies, depending on the ``max_font_size`` and the
		scaling heuristic.

	"""

	color_func: Callable
	"""
	Callable with parameters ``word``, ``font_size``, ``position``, ``orientation``,
	``font_path``, ``random_state`` which returns a PIL color for each word.
	"""

	def to_html(self):  # noqa: D102
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
			colormap: Union[None, str, Colormap] = None,
			repeat: bool = False,
			include_numbers: bool = False,
			min_word_length: int = 0,
			# margin=2,
			# ranks_only=None,
			random_state: Union[RandomState, int, None] = None,
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

	def __array__(self) -> numpy.ndarray:  # pragma: no cover (typed wrapper)
		"""
		Returns the wordcloud image as numpy array.
		"""

		return super().__array__()

	def generate_from_file(
			self,
			filename: PathLike,
			outfile: Optional[PathLike] = None,
			*,
			exclude_words: Sequence[str] = (),
			max_font_size: Optional[int] = None
			) -> "Wordle":
		"""
		Create a word_cloud from a source code file.

		:param filename: The file to process
		:param outfile: The file to save the wordle as. Supported formats are ``PNG``, ``JPEG`` and ``SVG``.
			If :py:obj:`None` the wordle is not saved
		:param exclude_words: An optional list of words to exclude
		:param max_font_size: Use this font-size instead of :attr:`~Wordle.max_font_size`.

		.. versionchanged:: 0.2.1  ``exclude_words``, ``max_font_size`` are now keyword-only.
		"""

		word_counts = frequency_from_file(filename, exclude_words)

		self.generate_from_frequencies(word_counts, max_font_size=max_font_size)

		if outfile:
			export_wordcloud(self, outfile)

		return self

	def generate_from_directory(
			self,
			directory: PathLike,
			outfile: Optional[PathLike] = None,
			*,
			exclude_words: Sequence[str] = (),
			exclude_dirs: Sequence[PathLike] = (),
			max_font_size: Optional[int] = None
			) -> "Wordle":
		"""
		Create a word_cloud from a directory of source code files.

		:param directory: The directory to process
		:param outfile: The file to save the wordle as. Supported formats are ``PNG``, ``JPEG`` and SVG.
			If :py:obj:`None` the wordle is not saved.
		:param exclude_words: An optional list of words to exclude
		:param exclude_dirs: An optional list of directories to exclude.
			Each entry is treated as a regular expression to match at the beginning of the relative path.
		:param max_font_size: Use this font-size instead of :attr:`~Wordle.max_font_size`.

		.. versionchanged:: 0.2.1  ``exclude_words``, ``exclude_dirs``, ``max_font_size`` are now keyword-only.
		"""

		word_counts: typing.Counter[str] = frequency_from_directory(
				directory,
				exclude_words=exclude_words,
				exclude_dirs=exclude_dirs,
				)

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
			*,
			sha: Optional[str] = None,
			depth: Optional[int] = None,
			exclude_words: Sequence[str] = (),
			exclude_dirs: Sequence[PathLike] = (),
			max_font_size: Optional[int] = None
			) -> "Wordle":
		"""
		Create a word_cloud from a directory of source code files.

		:param git_url: The url of the git repository to process
		:param outfile: The file to save the wordle as. Supported formats are ``PNG``, ``JPEG`` and SVG.
			If :py:obj:`None` the wordle is not saved
		:param sha: An optional SHA hash of a commit to checkout.
		:param depth: An optional depth to clone at. If :py:obj:`None` and ``sha`` is :py:obj:`None` the depth is ``1``.
			If :py:obj:`None` and ``sha`` is given the depth is unlimited.
		:param exclude_words: An optional list of words to exclude.
		:param exclude_dirs: An optional list of directories to exclude.
		:param max_font_size: Use this font-size instead of self.max_font_size.

		.. versionchanged:: 0.2.1

			* ``exclude_words``, ``exclude_dirs``, ``max_font_size`` are now keyword-only.
			* Added the ``sha`` and ``depth`` keyword-only arguments.
		"""

		with _TemporaryDirectory() as tmpdir:
			clone_into_tmpdir(git_url, tmpdir, sha=sha, depth=depth)

			self.generate_from_directory(
					tmpdir,
					outfile=outfile,
					exclude_dirs=exclude_dirs,
					exclude_words=exclude_words,
					max_font_size=max_font_size,
					)

			if sys.platform == "win32":
				time.sleep(5)  # pragma: no cover (!Windows)

		return self

	def recolor(  # pragma: no cover (typed wrapper)
		self,
		random_state: Union[RandomState, int, None] = None,
		color_func: Optional[Callable] = None,
		colormap: Union[None, str, Colormap] = None,
		) -> "Wordle":
		"""
		Recolour the existing layout.

		Applying a new coloring is much faster than regenerating the whole wordle.

		:param random_state: If not :py:obj:`None`, a fixed random state is used.
			If an :class:`int` is given, this is used as seed for a :class:`random.Random` state.
		:param color_func:  Function to generate new color from word count, font size, position and orientation.
			If :py:obj:`None`, :attr:`~Wordle.color_func` is used.
		:param colormap: Use this colormap to generate new colors.
			Ignored if ``color_func`` is specified. If :py:obj:`None`,
			:attr:`~Wordle.color_func` or :attr:`~Wordle.color_map` is used.

		:returns: self
		"""

		return super().recolor(random_state, color_func, colormap)

	def to_array(self):  # pragma: no cover (typed wrapper)
		"""
		Returns the wordcloud image as numpy array.
		"""

		return super().to_array()

	def to_file(self, filename: PathLike):
		"""
		Export the wordle to a file.

		:param filename: The file to save as.

		:returns: self
		"""

		return super().to_file(os.fspath(filename))

	def to_image(self):
		"""
		Returns the wordcloud as an image.
		"""

		return super().to_image()

	def to_svg(
			self,
			*,
			embed_font: bool = False,
			optimize_embedded_font: bool = True,
			embed_image: bool = False,
			) -> str:
		"""
		Export the wordle to an SVG.

		:param embed_font: Whether to include font inside resulting SVG file.
		:param optimize_embedded_font: Whether to be aggressive when embedding a font, to reduce size.
			In particular, hinting tables are dropped, which may introduce slight
			changes to character shapes (w.r.t. `to_image` baseline).
		:param embed_image: Whether to include rasterized image inside resulting SVG file.
			Useful for debugging.

		:returns: The content of the SVG image.
		"""

		return super().to_svg(embed_font, optimize_embedded_font, embed_image)


def export_wordcloud(word_cloud: WordCloud, outfile: PathLike) -> None:
	"""
	Export a wordcloud to a file.

	:param word_cloud:
	:param outfile: The file to export the wordcloud to.
	"""

	outfile = pathlib.Path(outfile)

	if outfile.suffix == ".svg":
		outfile.write_text(word_cloud.to_svg())
	else:
		word_cloud.to_file(str(outfile))
