#!/usr/bin/env python
#
#  utils.py
"""
Utility functions.

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
import os
import pathlib
import sys
import tempfile
from contextlib import redirect_stderr, suppress
from typing import ContextManager, Optional

# 3rd party
from domdf_python_tools.compat import nullcontext
from domdf_python_tools.typing import PathLike
from dulwich.config import StackedConfig
from southwark import clone, windows_clone_helper

__all__ = ["clone_into_tmpdir"]


def clone_into_tmpdir(
		git_url: str,
		tmpdir: PathLike,
		sha: Optional[str] = None,
		depth: Optional[int] = None,
		) -> pathlib.Path:
	"""
	Clone the git repository at ``git_url`` into ``tmpdir``.

	:param git_url: The url of the git repository to process
	:param tmpdir:
	:param sha: An optional SHA hash of a commit to checkout.
	:param depth: An optional depth to clone at. If :py:obj:`None` and ``sha`` is :py:obj:`None` the depth is ``1``.
		If :py:obj:`None` and ``sha`` is given the depth is unlimited.

	.. versionadded:: 0.2.0
	"""

	if sha is None and depth is None:
		depth = 1

	directory = pathlib.Path(tmpdir)

	_environ = dict(os.environ)  # or os.environ.copy()
	_default_backends = StackedConfig.default_backends

	with windows_clone_helper():
		with open(os.devnull) as devnull:
			with redirect_stderr(devnull):
				repo = clone(git_url, target=str(directory), depth=depth)

		if sha is not None:
			repo.reset_to(sha)

	return directory


class _TemporaryDirectory(tempfile.TemporaryDirectory):

	def cleanup(self):
		context: ContextManager

		if sys.platform == "win32":
			context = suppress(PermissionError, NotADirectoryError)
		else:
			context = nullcontext()

		with context:
			super().cleanup()
