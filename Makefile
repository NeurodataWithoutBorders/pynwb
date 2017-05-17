init:
	pip install -r requirements.txt

build:
	python3 setup.py build

install: build
	python3 setup.py install

develop: build
	python3 setup.py develop

test:
	python3 test.py

coverage:
	coverage3 run --source=. test.py

coverage_html: coverage
	coverage3 html -d tests/coverage/htmlcov
