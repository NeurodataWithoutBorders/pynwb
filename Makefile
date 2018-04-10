PYTHON = python
FLAKE = flake8
COVERAGE = coverage

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  init           to install required packages"
	@echo "  build          to build the python package(s)"
	@echo "  install        to build and install the python package(s)"
	@echo "  develop        to build and install the python package(s) for development"
	@echo "  test           to run all integration and unit tests"
	@echo "  htmldoc        to make the HTML documentation and open it with the default browser"
	@echo "  coverage       to run tests, build coverage HTML report and open it with the default browser"
	@echo ""
	@echo "Advanced targets"
	@echo "  apidoc         to generate API docs *.rst files from sources"
	@echo "  coverage-only  to run tests and build coverage report"
	@echo "  coverage-open  to open coverage HTML report in the default browser"
	@echo "  htmlclean      to remove all generated documentation"
	@echo "  htmldoc-only   to make the HTML documentation"
	@echo "  htmldoc-open   to open the HTML documentation with the default browser"
	@echo "  pdfdoc         to make the LaTeX sources and build the PDF of the documentation"

init:
	pip install -r requirements.txt -r requirements-dev.txt -r requirements-doc.txt

build:
	$(PYTHON) setup.py build

install: build
	$(PYTHON) setup.py install

develop: build
	$(PYTHON) setup.py develop

test:
	pip install -r requirements-dev.txt
	tox

flake:
	$(FLAKE) src/
	$(FLAKE) tests/
	$(FLAKE) --ignore E402 docs/gallery

checkpdb:
	find {src,tests} -name "*.py" -exec grep -Hn pdb {} \;

devtest:
	$(PYTHON) -W ignore test.py
	$(MAKE) flake
	$(MAKE) checkpdb

apidoc:
	pip install -r requirements-doc.txt
	cd docs && $(MAKE) apidoc

htmldoc-only: apidoc
	cd docs && $(MAKE) html

htmlclean:
	cd docs && $(MAKE) clean

htmldoc-open:
	@echo ""
	@echo "To view the HTML documentation open: docs/_build/html/index.html"
	open docs/_build/html/index.html || xdg-open docs/_build/html/index.html

htmldoc: htmldoc-only htmldoc-open

pdfdoc:
	cd docs && $(MAKE) latexpdf
	@echo ""
	@echo "To view the PDF documentation open: docs/_build/latex/PyNWB.pdf"

coverage-only:
	tox -e localcoverage

coverage-open:
	@echo "To view coverage data open: ./tests/coverage/htmlcov/index.html"
	open ./tests/coverage/htmlcov/index.html || xdg-open ./tests/coverage/htmlcov/index.html

coverage: coverage-only coverage-open
