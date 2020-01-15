..  _getting_started:

------------
Dependencies
------------

PyNWB has the following minimum requirements, which must be installed before you can get started using PyNWB.

#. Python 3.5, 3.6, or 3.7
#. pip

------------
Installation
------------

Install release from PyPI
-------------------------

The `Python Package Index (PyPI) <https://pypi.org>`_ is a repository of software for the Python programming language.

To install or update PyNWB distribution from PyPI simply run:

.. code::

   $ pip install -U pynwb

This will automatically install the following required dependencies:

 #. hdmf
 #. h5py
 #. numpy
 #. pandas
 #. python-dateutil


Install release from Conda-forge
--------------------------------

`Conda-forge <https://conda-forge.org/#about>`_ is a community led collection of recipes, build infrastructure
and distributions for the `conda <https://conda.io/docs/>`_ package manager.

To install or update PyNWB distribution from conda-forge using conda simply run:

.. code::

   $ conda install -c conda-forge pynwb


Install latest pre-release
--------------------------

This is useful to try out the latest features and also set up continuous integration of your
own project against the latest version of PyNWB.

.. code::

   $ pip install -U pynwb --find-links https://github.com/NeurodataWithoutBorders/pynwb/releases/tag/latest  --no-index


--------------
For developers
--------------

Install from Git repository
---------------------------

For development an editable install is recommended.

.. code::

   $ pip install -U virtualenv
   $ virtualenv ~/pynwb
   $ source ~/pynwb/bin/activate
   $ git clone --recurse-submodules git@github.com:NeurodataWithoutBorders/pynwb.git
   $ cd pynwb
   $ pip install -r requirements.txt
   $ pip install -e .


Run tests
---------

For running the tests, it is required to install the development requirements.

.. code::

   $ pip install -U virtualenv
   $ virtualenv ~/pynwb
   $ source ~/pynwb/bin/activate
   $ git clone --recurse-submodules git@github.com:NeurodataWithoutBorders/pynwb.git
   $ cd pynwb
   $ pip install -r requirements.txt -r requirements-dev.txt
   $ pip install -e .
   $ tox


Following PyNWB Style Guide
---------------------------

Before you create a Pull Request, make sure you are following PyNWB style guide (`PEP8 <https://www.python.org/dev/peps/pep-0008/>`_). To do that simply run
the following command in the project's root directory.

.. code::

   $ flake8
