.. _getting_started:

===============
Getting Started
===============


---------------
Prerequisites
---------------

PyNWB has the following minimum requirements, which must be installed before you can get started using PyNWB.

#. Python 3.x
#. HDF5
#. MPI


The NWB format provides a formal specification for storing neurophysiology data in HDF5. HDF5 provides support
for parallel I/O using MPI-IO, and therefore requires MPI.

---------------
Installation
---------------

PyNWB can be obtained by checking out the Git repository hosted on BitBucket `here <https://bitbucket.org/lblneuro/pynwb>`_.
Execute the following commands should install PyNWB.

.. code-block:: console

    $ git clone git@bitbucket.org:lblneuro/pynwb.git
    $ cd pynwb
    $ python setup.py build
    $ python setup.py install


Once installed, run the following tests to ensure that the installation worked.

.. code-block:: console

    $ python test.py
