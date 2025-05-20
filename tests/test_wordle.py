# stdlib
import io
from functools import partial
from pathlib import Path
from typing import Mapping, Optional, Sequence, Union

# 3rd party
import PIL  # type: ignore[import]
import pytest
from apeye.requests_url import RequestsURL
from coincidence.selectors import min_version, only_version
from domdf_python_tools.paths import PathPlus
from PIL import Image
from pytest_regressions.common import perform_regression_check
from pytest_regressions.data_regression import DataRegressionFixture
from pytest_regressions.image_regression import ImageRegressionFixture

# this package
from wordle import Wordle, export_wordcloud, frequency_from_file
from wordle.frequency import frequency_from_git

examples_dir = PathPlus(__file__).parent.parent / "examples"
src_dir = PathPlus(__file__).parent.parent / "wordle"

PILLOW_VERSION = int(''.join(PIL.__version__.split('.')[:2]))

pillow_version_params = pytest.mark.parametrize(
		"pillow_version",
		[
				pytest.
				param(81, marks=pytest.mark.skipif(PILLOW_VERSION >= 82, reason="Output differs on pillow 8.2.x")),
				pytest.param(
						82, marks=pytest.mark.skipif(PILLOW_VERSION < 82, reason="Output differs on pillow 8.2.x")
						),
				]
		)


class CounterRegressionFixture(DataRegressionFixture):

	def check(
			self,
			data_dict: Union[Sequence, Mapping],
			basename: Optional[str] = None,
			fullpath: Optional[str] = None,
			) -> None:
		super().check(dict(data_dict), basename=basename, fullpath=fullpath)


@pytest.fixture()
def counter_regression(datadir, original_datadir, request):
	return CounterRegressionFixture(datadir, original_datadir, request)


@pillow_version_params
def test_c_source_file(
		pillow_version,
		tmp_pathplus: PathPlus,
		image_regression: ImageRegressionFixture,
		counter_regression: CounterRegressionFixture,
		):
	w = Wordle(random_state=5678)

	src_file = examples_dir / "example.c"
	outfile = tmp_pathplus / "c_wordcloud.png"

	w.generate_from_file(src_file, outfile=tmp_pathplus / "c_wordcloud.svg")
	export_wordcloud(w, outfile=outfile)

	image_regression.check(outfile.read_bytes())
	counter_regression.check(frequency_from_file(src_file))


@pillow_version_params
@pytest.mark.usefixtures("pillow_version")
def test_python_source_file(
		tmp_pathplus: PathPlus,
		image_regression: ImageRegressionFixture,
		counter_regression: CounterRegressionFixture,
		):
	w = Wordle(random_state=5678)

	outfile = tmp_pathplus / "python_wordcloud.png"

	source_url = RequestsURL("https://raw.githubusercontent.com/domdfcoding/wordle")
	source_url = source_url / "76797ba8b641b38fe1bed0801f0af248b793b59e/wordle/__init__.py"
	(tmp_pathplus / "source.py").write_bytes(source_url.get().content)

	w.generate_from_file(tmp_pathplus / "source.py", outfile=tmp_pathplus / "python_wordcloud.svg")
	export_wordcloud(w, outfile=outfile)

	image_regression.check(outfile.read_bytes())
	counter_regression.check(frequency_from_file(tmp_pathplus / "source.py"))


@pillow_version_params
def test_github_repo(
		pillow_version,
		tmp_pathplus: PathPlus,
		image_regression: ImageRegressionFixture,
		):
	w = Wordle(random_state=5678)

	w.generate_from_git(
			"https://github.com/domdfcoding/domdf_python_tools",
			outfile=tmp_pathplus / "git_wordcloud.svg",
			sha="de815f593718e16c031bc70e9c24b5635c3144dc",
			)
	export_wordcloud(w, outfile=tmp_pathplus / "git_wordcloud.png")

	image_regression.check((tmp_pathplus / "git_wordcloud.png").read_bytes(), diff_threshold=3.5)

	# The results should be different for a different commit
	w.generate_from_git(
			"https://github.com/domdfcoding/domdf_python_tools",
			outfile=tmp_pathplus / "git_wordcloud.svg",
			sha="c30106567a27a17a5bd1339409ca22b6d425a25f",
			)
	export_wordcloud(w, outfile=tmp_pathplus / "git_wordcloud.png")

	with pytest.raises(AssertionError, match="Difference between images too high"):
		image_regression.check((tmp_pathplus / "git_wordcloud.png").read_bytes(), diff_threshold=3.5)


@pillow_version_params
@pytest.mark.usefixtures("pillow_version")
def test_github_repo_exclude_tests(
		tmp_pathplus: PathPlus,
		image_regression: ImageRegressionFixture,
		):
	w = Wordle(random_state=5678)

	w.generate_from_git(
			"https://github.com/domdfcoding/domdf_python_tools",
			outfile=tmp_pathplus / "git_wordcloud.svg",
			sha="de815f593718e16c031bc70e9c24b5635c3144dc",
			exclude_dirs=["tests"]
			)
	export_wordcloud(w, outfile=tmp_pathplus / "git_wordcloud.png")

	image_regression.check((tmp_pathplus / "git_wordcloud.png").read_bytes(), diff_threshold=3.5)


@pillow_version_params
@pytest.mark.usefixtures("pillow_version")
def test_github_repo_exclude_words(
		tmp_pathplus: PathPlus,
		image_regression: ImageRegressionFixture,
		):
	w = Wordle(random_state=5678)

	w.generate_from_git(
			"https://github.com/domdfcoding/domdf_python_tools",
			outfile=tmp_pathplus / "git_wordcloud.svg",
			sha="de815f593718e16c031bc70e9c24b5635c3144dc",
			exclude_words=["assert", "def", "self"]
			)
	export_wordcloud(w, outfile=tmp_pathplus / "git_wordcloud.png")

	image_regression.check((tmp_pathplus / "git_wordcloud.png").read_bytes(), diff_threshold=3.5)


@pytest.mark.parametrize(
		"python_version",
		[
				pytest.param(
						"3.6", marks=only_version(3.6, reason="Output differs with older Pygments on Python 3.6")
						),
				pytest.param(
						"3.7", marks=min_version(3.6, reason="Output differs with older Pygments on Python 3.6")
						),
				]
		)
@pytest.mark.usefixtures("python_version")
def test_github_repo_frequency(counter_regression: CounterRegressionFixture):
	frequency = frequency_from_git(
			"https://github.com/domdfcoding/domdf_python_tools",
			sha="de815f593718e16c031bc70e9c24b5635c3144dc",
			exclude_words=["assert", "def", "self"]
			)
	counter_regression.check(frequency)
