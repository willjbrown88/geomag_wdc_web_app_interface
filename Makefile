.PHONY: clean-pyc clean-build docs clean
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "develop - installs package and dependencies locally and links to site-packages, local file changes get propagated to app without reinsall"
	@echo "install - install the package to the active Python's site-packages; may install a CLI app too"
	@echo "uninstall - uninstall the package by name, with pip."
	@echo "all - cleans, installs, runs tests and builds docs."

clean: clean-build clean-pyc clean-test

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -f .coverage
	rm -fr htmlcov/

lint:
	flake8 lib tests || true  # prevent terminate on fail
	pylint lib tests

test:
	pytest

coverage:
	pytest --cov-report html --cov lib tests
	$(BROWSER) htmlcov/index.html

docs:
	rm -f docs/lib*.rst
	rm -f docs/lib/lib.rst
	rm -f docs/lib/modules.rst
	sphinx-apidoc -o docs/lib/ lib
	ln -s docs/lib/lib*.rst docs/
	$(MAKE) -C docs/ clean
	$(MAKE) -C docs/ html
	$(BROWSER) docs/_build/html/index.html

install: clean
	pip install .

develop: clean
	pip install -e .[$@]

uninstall:
	pip uninstall geomag-wdc-web-app-interface

all: clean install test docs
