# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import versioneer

import configparser
from os.path import join as pjoin


def get_schema_sha(url_path):
    parser = configparser.RawConfigParser()
    config_path = pjoin('.git', 'modules', 'src', 'pynwb', 'nwb-schema', 'config')
    parser.read(config_path)
    url = parser.get('remote "origin"', 'url')
    sha_path = pjoin('.git', 'modules', 'src', 'pynwb', 'nwb-schema', 'HEAD')
    sha = open(sha_path, 'r').read()[:-1]
    url = "%s/tree/%s" % (url[:-4], sha)
    with open(url_path, 'w') as f:
        print(url, file=f)


schema_url_path = pjoin('src', 'pynwb', 'core_schema_url')
print('writing schema URL to %s' % schema_url_path)
get_schema_sha(schema_url_path)

with open('README.rst', 'r') as fp:
    readme = fp.read()

pkgs = find_packages('src', exclude=['data'])
print('found these packages:', pkgs)

schema_dir = 'nwb-schema/core'

with open('requirements-min.txt', 'r') as fp:
    # replace == with >= and remove trailing comments and spaces
    reqs = [x.replace('==', '>=').split('#')[0].strip() for x in fp]
    reqs = [x for x in reqs if x]  # remove empty strings

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
    'package_data': {'pynwb': ["%s/*.yaml" % schema_dir, "%s/*.json" % schema_dir, schema_url_path]},
    'classifiers': [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
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
    'zip_safe': False
}

if __name__ == '__main__':
    setup(**setup_args)
