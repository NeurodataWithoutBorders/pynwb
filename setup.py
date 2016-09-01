# -*- coding: utf-8 -*-

from dist import setup, find_packages


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

