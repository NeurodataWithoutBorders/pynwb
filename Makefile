init:
	pip install -r requirements.txt

build:
	python3 setup.py build

install:
	python3 setup.py install

develop:
	python3 setup.py develop

test:
	python3 test.py
