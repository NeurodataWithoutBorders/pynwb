..  _install_developers:

-------------------------------
Installing PyNWB for Developers
-------------------------------

PyNWB has the following minimum requirements, which must be installed before you can get started using PyNWB.

#. Python 3.8, 3.9, 3.10, or 3.11
#. pip


Set up a virtual environment
----------------------------

For development, we recommend installing PyNWB in a virtual environment in editable mode. You can use
the virtualenv_ tool to create a new virtual environment. Or you can use the
`conda package and environment management system`_ for managing virtual environments.

.. _virtualenv: https://virtualenv.pypa.io/en/stable/
.. _conda package and environment management system: https://conda.io/projects/conda/en/latest/index.html

Option 1: Using virtualenv
^^^^^^^^^^^^^^^^^^^^^^^^^^

First, install the latest version of the ``virtualenv`` tool and use it to create a new virtual environment. This
virtual environment will be stored in the ``venv`` directory in the current directory.

.. code:: bash

    pip install -U virtualenv
    virtualenv venv

On macOS or Linux, run the following to activate your new virtual environment:

.. code:: bash

    source venv/bin/activate

On Windows, run the following to activate your new virtual environment:

.. code:: batch

    venv\Scripts\activate

This virtual environment is a space where you can install Python packages that are isolated from other virtual
environments. This is especially useful when working on multiple Python projects that have different package
requirements and for testing Python code with different sets of installed packages or versions of Python.

Activate your newly created virtual environment using the above command whenever you want to work on HDMF. You can also
deactivate it using the ``deactivate`` command to return to the base environment.

Option 2: Using conda
^^^^^^^^^^^^^^^^^^^^^

First, install Anaconda_ to install the ``conda`` tool. Then create and
activate a new virtual environment called "venv" with Python 3.8 installed.

.. code:: bash

    conda create --name venv python=3.8
    conda activate venv

Similar to a virtual environment created with ``virtualenv``, a conda environment
is a space where you can install Python packages that are isolated from other virtual
environments. In general, you should use ``conda install`` instead of ``pip install`` to install packages
in a conda environment.

Activate your newly created virtual environment using the above command whenever you want to work on HDMF. You can also
deactivate it using the ``conda deactivate`` command to return to the base environment.

.. _Anaconda: https://www.anaconda.com/distribution


Install from Git repository
---------------------------

After you have created and activated a virtual environment, clone the PyNWB git repository from GitHub, install the
package requirements using the `pip <https://pip.pypa.io/en/stable/>`_ Python package manager, and install PyNWB in
editable mode.

.. code:: bash

    git clone --recurse-submodules https://github.com/NeurodataWithoutBorders/pynwb.git
    cd pynwb
    pip install -r requirements.txt -r requirements-dev.txt
    pip install -e .


Run tests
---------

For running the tests, it is required to install the development requirements. Again, first activate your
virtualenv or conda environment.

.. code:: bash

    git clone --recurse-submodules https://github.com/NeurodataWithoutBorders/pynwb.git
    cd pynwb
    pip install -r requirements.txt -r requirements-dev.txt
    pip install -e .
    tox

For debugging it can be useful to keep the intermediate NWB files created by
the tests. To keep these files create the environment variables
``CLEAN_NWB``/``CLEAN_HDMF`` and set them to ``1``.


FAQ
---

1.  I am using a git cloned copy of PyNWB and getting the error:
    ``RuntimeError: Unable to load a TypeMap - no namespace file found``

    or the error:
    ``RuntimeError: 'core' is not a registered namespace.``

    - The PyNWB repo uses git submodules that have to be checked out when cloning the repos. Please make sure you
      are using the ``--recurse-submodules`` flag when running ``git clone``:

      .. code-block:: bash

          git clone --recurse-submodules https://github.com/NeurodataWithoutBorders/pynwb.git

      You can also run the following on your existing cloned repo.

      .. code-block:: bash

          git submodule init
          git submodule update --checkout --force

2.  I did a ``git pull`` but I'm getting errors that some ``neurodata_type`` does not exist.

    - The PyNWB repo uses git submodules that have to be updated as well. Please make sure you
      are using the ``git pull --recurse-submodules``
