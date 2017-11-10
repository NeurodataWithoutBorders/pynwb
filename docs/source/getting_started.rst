..  _getting_started:

===============
Getting Started
===============

------------
Dependencies
------------

PyNWB has the following minimum requirements, which must be installed before you can get started using PyNWB.

#. Python 2.7 or Python 3.6
#. pip

The NWB format provides a formal specification for storing neurophysiology data in HDF5. HDF5 provides support
for parallel I/O using MPI-IO, and therefore requires MPI.

------------
Installation
------------

Install from pypi
-----------------

To install or update PyNWB distribution from PyPI simply run:

.. code::

   $ pip install -U pynwb

This will automatically install the following required dependencies:

 #. h5py
 #. numpy
 #. python-dateutil
 #. requests
 #. ruamel.yaml
 #. six

Install latest dev version
--------------------------

.. note::

  This is useful to tryout the latest features and also setup automatic build of your
  own project against the latest version of pynwb.

.. code::

   $ pip install pynwb --find-links https://github.com/NeurodataWithoutBorders/pynwb/releases/tag/latest  --no-index

Install from Git repository (for development)
---------------------------------------------

For development an editable install is recommended.

.. code::

   $ pip install -U virtualenv
   $ virtualenv ~/pynwb
   $ ~/pynwb/bin/activate
   $ git clone git@github.com:NeurodataWithoutBorders/pynwb.git
   $ cd pynwb
   $ pip install -r requirements.txt -r requirements-dev.txt
   $ pip install -e .


Run tests
---------

For running the tests, it is required to install the development requirements.

.. code::

   $ pip install -U virtualenv
   $ virtualenv ~/pynwb
   $ ~/pynwb/bin/activate
   $ git clone git@github.com:NeurodataWithoutBorders/pynwb.git
   $ cd pynwb
   $ pip install -r requirements.txt -r requirements-dev.txt
   $ pip install -e .
   $ tox
