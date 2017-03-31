# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.build_py import build_py

from urllib.request import urlretrieve
import json
import pickle
import os
from tarfile import TarFile


class CustomBuild(build_py):
    def run(self):
        '''Here, we will do something to access a URL stored in the pynwb repo.
        This URL will contain the source of the schema.
        '''
        # we should look this up in a config file somewhere
        schema_dir = '%s/src/pynwb/data' % os.path.abspath(os.path.dirname(__file__))
        if not os.path.exists(schema_dir):
            os.makedirs(schema_dir)
        url = "https://bitbucket.org/lblneuro/nwb-schema/downloads/nwb_core.tar"
        dest = "nwb_core.tar"
        schema = urlretrieve(url, dest)
        tf = TarFile(dest, 'r')
        tf.extractall(schema_dir)
        super(CustomBuild, self).run()



with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


pkgs=['pynwb',
      'pynwb.io' ]

setup_args = {
    'name': 'pynwb',
    'version': '0.0.1',
    'description': 'Package for working with Neurodata stored in the NWB format',
    'long_description': readme,
    'author': 'Andrew Tritt',
    'author_email': 'ajtritt@lbl.gov',
    'url': 'https://bitbucket.org/lblneuro/pynwb',
    'license': license,
    'packages': pkgs,
    'package_dir': {'': 'src'},
    #'package_data': {'pynwb':[schema_dir]}
    'cmdclass':{
        'build_py': CustomBuild,
    }
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


