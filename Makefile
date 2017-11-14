PYTHON = python
COVERAGE = coverage

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  init           to install required packages"
	@echo "  build          to build the python package(s)"
	@echo "  install        to build and install the python package(s)"
	@echo "  develop        to build and install the python package(s) for development"
	@echo "  test           to run all unit tests"
	@echo "  htmldoc        to make the HTML documentation"
	@echo "  pdfdoc         to make the LaTeX sources and build the PDF of the documentation"
	@echo "  coverage       to run coverage"
	@echo "  coverage_html  to run coverage and build the coverage report in HTML"
	@echo ""

init:
	pip install -r requirements.txt

build:
	$(PYTHON) setup.py build

install: build
	$(PYTHON) setup.py install

develop: build
	$(PYTHON) setup.py develop

test:
	pip install -r requirements-dev.txt
	tox

test_docker:
	docker build --quiet --no-cache --tag neurodatawithoutborders/pynwb:python27_test -f ./docker/python27_test/Dockerfile .
	docker run --rm -it neurodatawithoutborders/pynwb:python27_test bash -c 'python test.py'
	docker build --quiet --no-cache --tag neurodatawithoutborders/pynwb:python35_test -f ./docker/python35_test/Dockerfile .
	docker run --rm -it neurodatawithoutborders/pynwb:python35_test bash -c 'python test.py'
	docker build --quiet --no-cache --tag neurodatawithoutborders/pynwb:python36_test -f ./docker/python36_test/Dockerfile .
	docker run --rm -it neurodatawithoutborders/pynwb:python36_test bash -c 'python test.py'

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

coverage:
	tox -e coverage

coverage-open:
	@echo "To view coverage data open: ./tests/coverage/htmlcov/index.html"
	open ./tests/coverage/htmlcov/index.html || xdg-open ./tests/coverage/htmlcov/index.html
