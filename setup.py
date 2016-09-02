# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='PyNWB',
    version='0.0.1',
    description='Package for working with Neurodata stored in the NWB format',
    long_description=readme,
    author='Andrew Tritt',
    author_email='ajtritt@lbl.gov',
    url='https://bitbucket.org/lblneuro/pynwb',
    license=license,
    #packages=find_packages(exclude=('tests', 'docs'))
    packages=['pynwb'],
    package_dir={'pynwb':'src/pynwb'},
    data_files=[('schema', ['schema/*.json'])]
)

'''
Do some stuff here to retrieve (download from centralized location, or parse
from a location in the repo directory) the schema. Once retrieved write to 
to Python code somewhere. This could be pickling it, or writing it to a 
Python file as an ecoded string. This way, modifying the schema will require
rebuilding the package, and the schema will be hardcoded.
'''
