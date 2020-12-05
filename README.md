# networkx-astar-path

![PyPI](https://img.shields.io/pypi/v/networkx-astar-path?style=flat-square)
![GitHub Workflow Status (master)](https://img.shields.io/github/workflow/status/escaped/networkx-astar-path/Test%20&%20Lint/master?style=flat-square)
![Coveralls github branch](https://img.shields.io/coveralls/github/escaped/networkx-astar-path/master?style=flat-square)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/networkx-astar-path?style=flat-square)
![PyPI - License](https://img.shields.io/pypi/l/networkx-astar-path?style=flat-square)

Alternative A* implementation, which provides the current and previous edge to the weight function.

## Requirements

* Python 3.6.1 or newer
* [poetry](https://poetry.eustance.io/) 1.1 or newer


## Development

This project uses [poetry](https://poetry.eustace.io/) for packaging and
managing all dependencies and [pre-commit](https://pre-commit.com/) to run
[flake8](http://flake8.pycqa.org/), [isort](https://pycqa.github.io/isort/),
[mypy](http://mypy-lang.org/) and [black](https://github.com/python/black).

Clone this repository and run

```bash
poetry install
poetry run pre-commit install
```

to create a virtual enviroment containing all dependencies.
Afterwards, You can run the test suite using

```bash
poetry run pytest
```

This repository follows the [Conventional Commits](https://www.conventionalcommits.org/)
style.

### Cookiecutter template

This project was created using [cruft](https://github.com/cruft/cruft) and the
[cookiecutter-pyproject](https://github.com/escaped/cookiecutter-pypackage) template.
In order to update this repository to the latest template version run

```sh
cruft update
```

in the root of this repository.

