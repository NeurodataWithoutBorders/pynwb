.. _getting_started:

===============
Getting Started
===============


---------------
Prerequisites
---------------

PyNWB has the following minimum requirements, which must be installed before you can get started using PyNWB.

#. Python 3.x

   * Before moving forward, make sure `setuptools <https://pypi.python.org/pypi/setuptools>`_ is installed with your version of Python.

#. HDF5
#. MPI


The NWB format provides a formal specification for storing neurophysiology data in HDF5. HDF5 provides support
for parallel I/O using MPI-IO, and therefore requires MPI.

---------------
Installation
---------------

PyNWB can be obtained by checking out the Git repository hosted on GitHub `here <https://github.com/NeurodataWithoutBorders/pynwb>`_.
Execute the following commands should install PyNWB.

.. code-block:: console

    $ git clone https://github.com/NeurodataWithoutBorders/pynwb.git
    $ cd pynwb
    $ git checkout dev              # This will not be required in the long-term
    $ python setup.py build
    $ python setup.py install


Once installed, run the following tests to ensure that the installation worked.

.. code-block:: console

    $ python test.py
