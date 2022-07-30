import pybotters
import toml


def test_version():
    with open("pyproject.toml", encoding="utf-8") as f:
        pyproject = toml.load(f)
    assert pybotters.__version__ == pyproject["tool"]["poetry"]["version"]
