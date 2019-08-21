# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from setuptools.command.build_py import build_py
import re

import versioneer

class BuildPyCommand(build_py):
    tm_pkl_path = 'typemap.pkl'
    def run(self):
        ########## BEGIN: PICKLE TYPE MAP
        import sys
        import os
        import pickle

        sys.path.append('src')
        import pynwb
        tm = pynwb.get_type_map()

        pkl_path = os.path.join('src', 'pynwb', self.tm_pkl_path)
        sys.stdout.write('pickling type map to %s\n' % pkl_path)
        with open(pkl_path, 'wb') as f:
            pickle.dump(tm, f, pickle.HIGHEST_PROTOCOL)
        ########## END: PICKLE TYPE MAP
        super().run()

with open('README.rst', 'r') as fp:
    readme = fp.read()

pkgs = find_packages('src', exclude=['data'])
print('found these packages:', pkgs)

schema_dir = 'nwb-schema/core'

reqs_re = re.compile("[<=>]+")
with open('requirements.txt', 'r') as fp:
    reqs = [reqs_re.split(x.strip())[0] for x in fp.readlines()]

print(reqs)

setup_args = {
    'name': 'pynwb',
    'version': versioneer.get_version(),
    'cmdclass': versioneer.get_cmdclass(),
    'description': 'Package for working with Neurodata stored in the NWB format',
    'long_description': readme,
    'long_description_content_type': 'text/x-rst; charset=UTF-8',
    'author': 'Andrew Tritt',
    'author_email': 'ajtritt@lbl.gov',
    'url': 'https://github.com/NeurodataWithoutBorders/pynwb',
    'license': "BSD",
    'install_requires': reqs,
    'packages': pkgs,
    'package_dir': {'': 'src'},
    #'package_data': {'pynwb': ["%s/*.yaml" % schema_dir, "%s/*.json" % schema_dir]},
    'package_data': {'pynwb': [BuildPyCommand.tm_pkl_path]},
    'classifiers': [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Topic :: Scientific/Engineering :: Medical Science Apps."
    ],
    'keywords': 'Neuroscience '
                'python '
                'HDF '
                'HDF5 '
                'cross-platform '
                'open-data '
                'data-format '
                'open-source '
                'open-science '
                'reproducible-research '
                'PyNWB '
                'NWB '
                'NWB:N '
                'NeurodataWithoutBorders',
    'zip_safe': False,
    'cmdclass': {'build_py': BuildPyCommand}
}

if __name__ == '__main__':
    setup(**setup_args)
