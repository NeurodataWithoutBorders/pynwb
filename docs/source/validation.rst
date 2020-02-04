.. _validating:

Validating NWB files
====================

Validating NWB files is handled by a command-line tool available in :py:mod:`~pynwb`. The validator can be invoked like so:

.. code-block:: bash

  python -m pynwb.validate test.nwb

This will validate the file ``test.nwb`` against the *core* NWB specification. In case of success the output looks like

.. code-block:: text

  Validating test.nwb against cached namespace information using namespace core.
   - no errors found.

and the program exit code is ``0``. On error the program exit code is ``1`` and
the list of errors is outputted.

If possible the file is validated against the cached namespace specification
read from the file itself. This can be tweaked with the command line options given below.

CURRENTLY BROKEN!!!

Validating against other specifications i.e. extensions
can be done using the ``-p`` and ``-n`` flags. For example, the following command will validate against the specifications referenced in the namespace
file ``mylab.namespace.yaml`` in addition to the core specification.

.. code-block:: bash

  python -m pynwb.validate -p mylab.namespace.yaml test.nwb

.. Last updated 2/2020
.. code-block:: text

  $python -m pynwb.validate --help
  usage: validate.py [-h] [-p NSPATH] [-n NS] [-lns]
                     [--cached-namespace | --no-cached-namespace]
                     paths [paths ...]

  Validate an NWB file

  positional arguments:
    paths                 NWB file paths

  optional arguments:
    -h, --help            show this help message and exit
    -p NSPATH, --nspath NSPATH
                          the path to the namespace YAML file
    -n NS, --ns NS        the namespace to validate against
    -lns, --list-namespaces
                          List the available namespaces and exit.
    --cached-namespace    Use the cached namespace (default).
    --no-cached-namespace
                          Don't use the cached namespace.

  use --nspath to validate against an extension. If --ns is not specified,
  validate against all namespaces in namespace file.
