# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import os


schema_dir = '%s/src/pynwb/data' % os.path.abspath(os.path.dirname(__file__))

with open('README.rst') as f:
    readme = f.read()

with open('license.txt') as f:
    license = f.read()


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
    'packages': pkgs,
    'package_dir': {'': 'src'},
    'package_data': {'pynwb':["%s/*.yaml" % schema_dir, "%s/*.json" % schema_dir]},
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
