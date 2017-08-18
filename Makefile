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
	$(PYTHON) test.py

test_docker:
	docker build --quiet --no-cache --tag neurodatawithoutborders/pynwb:python27_test -f ./docker/python27_test/Dockerfile .
	docker run --rm -it neurodatawithoutborders/pynwb:python27_test bash -c 'python test.py'

	docker build --quiet --no-cache --tag neurodatawithoutborders/pynwb:python35_test -f ./docker/python35_test/Dockerfile .
	docker run --rm -it neurodatawithoutborders/pynwb:python35_test bash -c 'python test.py'

apidoc:
	cd docs && $(MAKE) apidoc
	@echo ""
	@echo "To view the PDF documentation open: docs/_build/html/index.html"

htmldoc:
	cd docs && $(MAKE) html
	@echo ""
	@echo "To view the PDF documentation open: docs/_build/html/index.html"

pdfdoc:
	cd docs && $(MAKE) latexpdf
	@echo ""
	@echo "To view the PDF documentation open: docs/_build/latex/PyNWB.pdf"

coverage:
	$(COVERAGE) run --source=. test.py

coverage_html: coverage
	$(COVERAGE) html -d tests/coverage/htmlcov
	@echo ""
	@echo "To view coverage data open: tests/coverage/htmlcov/index.html"
