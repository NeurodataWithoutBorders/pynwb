# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py

import json
import pickle
import os


schema_dir = '%s/src/pynwb/data' % os.path.abspath(os.path.dirname(__file__))

with open('README.rst', 'rb') as f:
    readme = str(f.read())

with open('license.txt', 'rb') as f:
    license = str(f.read())


pkgs = find_packages('src', exclude=['data'])
print('found these packages:', pkgs)

schema_dir = 'data'

setup_args = {
    'name': 'pynwb',
    'version': '0.1',
    'description': 'Package for working with Neurodata stored in the NWB format',
    'long_description': readme,
    'author': 'Andrew Tritt',
    'author_email': 'ajtritt@lbl.gov',
    'url': 'https://github.com/NeurodataWithoutBorders/pynwb',
    'license': license,
    'install_requires':
    [
        'numpy',
        'h5py',
        'ruamel.yaml',
        'python-dateutil',
        'six',
        'requests'
    ],
    'packages': pkgs,
    'package_dir': {'': 'src'},
    'package_data': {'pynwb':["%s/*.yaml" % schema_dir, "%s/*.json" % schema_dir]},
    'classifiers': [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Topic :: Scientific/Engineering :: Medical Science Apps."
    ],
    'keywords':'PyNWB NWB Neuroscience HDF NeurodataWithoutBorders',
    #'package_data': {'pynwb':["data/*.yaml"]},
    #'cmdclass':{
    #    'build_py': CustomBuild,
    #}
}

if __name__ == '__main__':
    '''
    Do some stuff here to retrieve (download from centralized location, or parse
    from a location in the repo directory) the schema. Once retrieved write to
    to Python code somewhere. This could be pickling it, or writing it to a
    Python file as an ecoded string. This way, modifying the schema will require
    rebuilding the package, and the schema will be hardcoded.
    '''

    #get_schema()
    setup(**setup_args)
