#
# pynwb miniconda Dockerfile
#
# https://github.com/NeurodataWithoutBorders/pynwb
# http://pynwb.readthedocs.io/en/latest/index.html
#
# To run:
# - cd pynwb/docker
# - docker build --tag neurodatawithoutborders/pynwb:python27_test -f ./python27_test/Dockerfile ..

# Pull base image.
FROM continuumio/miniconda:latest

RUN apt-get update
USER root
SHELL ["/bin/bash", "-c"]

RUN conda update -y conda
RUN conda create -n python27 python=2.7
RUN source activate python27
COPY . /pynwb
WORKDIR /pynwb

RUN pip install -r 'requirements.txt'
RUN python setup.py build
RUN python setup.py install
RUN python test.py
