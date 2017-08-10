#
# dipde miniconda Dockerfile
#
# https://github.com/NeurodataWithoutBorders/pynwb
# http://pynwb.readthedocs.io/en/latest/index.html
#
# To run:
# - cd pynwb/docker
# - docker build --tag neurodatawithoutborders/pynwb:dev -f ./dev/Dockerfile ..

# Pull base image.
FROM continuumio/miniconda:latest

# Allows plotting tests
RUN apt-get update
USER root
SHELL ["/bin/bash", "-c"]

RUN conda update -y conda
RUN conda create -n python35 python=3.5
RUN source activate python35
WORKDIR /
RUN git clone https://github.com/NeurodataWithoutBorders/pynwb.git
WORKDIR /pynwb
RUN git checkout dev

RUN pip install -r 'requirements.txt'
RUN python setup.py build
RUN python setup.py install
RUN python test.py
