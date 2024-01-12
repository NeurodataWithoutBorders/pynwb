..  _install_users:

----------------
Installing PyNWB
----------------

PyNWB has the following minimum requirements, which must be installed before you can get started using PyNWB.

#. Python 3.8, 3.9, 3.10, or 3.11
#. pip

.. note:: If you are a developer then please see the :ref:`install_developers` installation instructions instead.

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

`Conda-forge <https://conda-forge.org>`_ is a community led collection of recipes, build infrastructure
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


