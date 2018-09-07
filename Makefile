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
	@echo "clean - remove all build, test, coverage, documentation, and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "clean-test - remove test and coverage artifacts"
	@echo "clean-docs - remove documentation artifacts"
	@echo "lint - check style with flake8 and pylint"
	@echo "test - run tests quickly with the default Python"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "develop - installs package and dependencies locally and links to site-packages, local file changes get propagated to app without reinstall"
	@echo "install - install the package to the active Python's site-packages; may install a CLI app too"
	@echo "uninstall - uninstall the package from the active environment, by name, with pip."
	@echo "all - cleans, installs, runs tests and builds docs."
	@echo "travis-install - the automatic build for Travis CI"

clean: clean-build clean-pyc clean-test clean-docs

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

clean-docs:
	rm -f docs/gmdata_webinterface/gmdata_webinterface.rst
	rm -f docs/gmdata_webinterface/modules.rst
	$(MAKE) -C docs/ clean

lint:
	flake8 gmdata_webinterface gmdata_webinterface/tests || true  # prevent terminate on fail
	pylint gmdata_webinterface gmdata_webinterface/tests

test:
	pytest

coverage:
	pytest --cov-report html --cov gmdata_webinterface gmdata_webinterface/tests
	$(BROWSER) htmlcov/index.html

docs: clean-docs
	sphinx-apidoc -o docs/gmdata_webinterface/ gmdata_webinterface
	$(MAKE) -C docs/ html
	$(BROWSER) docs/.build/html/index.html

install: clean
	pip install .

develop: clean
	pip install -e .[$@]

uninstall:
	pip uninstall gmdata_webinterface

all: install test docs

travis-install:
	pip install .
