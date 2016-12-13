# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from urllib.request import urlopen
import json
import pickle


def get_schema():
    '''Here, we will do something to access a URL stored in the pynwb repo.
    This URL will contain the source of the schema.  
    '''
    # we should look this up in a config file somewhere
    url = "https://bitbucket.org/lblneuro/nwb-schema/downloads/nwb_1.0.4_beta.json"
    schema = urlopen(url)
    return schema

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

    
schema_path = 'schema/schema.pkl'

setup_args = {
    'name': 'PyNWB',
    'version': '0.0.1',
    'description': 'Package for working with Neurodata stored in the NWB format',
    'long_description': readme,
    'author': 'Andrew Tritt',
    'author_email': 'ajtritt@lbl.gov',
    'url': 'https://bitbucket.org/lblneuro/pynwb',
    'license': license,
    #'packages': find_packages(exclude=('tests', 'docs'))
    'packages': ['pynwb'],
    'package_dir': {'pynwb':'src/pynwb'},
    'package_data': {'pynwb':[schema_path]}
}

if __name__ == '__main__':
    '''
    Do some stuff here to retrieve (download from centralized location, or parse
    from a location in the repo directory) the schema. Once retrieved write to 
    to Python code somewhere. This could be pickling it, or writing it to a 
    Python file as an ecoded string. This way, modifying the schema will require
    rebuilding the package, and the schema will be hardcoded.
    '''
    schema = get_schema()
    with open(schema_path,'w') as schema_out:
        pickle.dump(schema, schema_out)

    setup(**setup_args)


