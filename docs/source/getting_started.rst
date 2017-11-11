..  _getting_started:

------------
Dependencies
------------

PyNWB has the following minimum requirements, which must be installed before you can get started using PyNWB.

#. Python 2.7, Python 3.5 or Python 3.6
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

 #. h5py
 #. numpy
 #. python-dateutil
 #. requests
 #. ruamel.yaml
 #. six


Install latest pre-release
--------------------------

This is useful to tryout the latest features and also setup continuous integration of your
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


Following PyNWB Style Guide
---------------------------

Before you create a Pull Request, make sure you are following PyNWB style guide (`PEP8 <https://www.python.org/dev/peps/pep-0008/>`_). To do that simply run
the following command in the project's root directory.

.. code::

   $ flake8
