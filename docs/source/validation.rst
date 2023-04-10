.. _validating:

Validating NWB files
====================

Validating NWB files is handled by a command-line tool available after installing ``pynwb``.
The validator can be invoked like so:

.. code-block:: bash

  validate_nwb test.nwb

If the file contains no NWB extensions, then this command will validate the file ``test.nwb`` against the
*core* NWB specification. On success, the output will is:

.. code-block:: text

  Validating test.nwb against cached namespace information using namespace 'core'.
   - no errors found.

and the program exit code is ``0``. On error, the program exit code is ``1`` and the list of errors is outputted.

If the file contains NWB extensions, then the above validation command will validate the file ``test.nwb`` against
all extensions in the file and the core NWB specification.

To validate against only one NWB extension that is cached within the file, use the ``-n`` flag.
For example, the following command will validate against the "ndx-my-extension" namespace that is cached
within the ``test.nwb`` file.

.. code-block:: bash

  validate_nwb -n ndx-my-extension test.nwb

To validate against the version of the **core** NWB specification that is included with the installed version of
PyNWB, use the ``--no-cached-namespace`` flag. This can be useful in validating files against newer or older versions
of the **core** NWB specification that are installed with newer or older versions of PyNWB.

.. code-block:: bash

  validate_nwb --no-cached-namespace test.nwb

.. Last updated 4/10/2023
.. code-block:: text

  $ validate_nwb --help
  usage: validate_nwb [-h] [-l] [-n NS] [--no-cached-namespace] paths [paths ...]

  Validate one or more NWB files

  positional arguments:
    paths                 NWB file path(s)

  options:
    -h, --help            show this help message and exit
    -l, --list-namespaces
                          List the available namespaces and exit.
    -n NS, --ns NS        the namespace to validate against
    --no-cached-namespace
                          Use the namespace installed with PyNWB (2.6.0) instead of the cached
                          namespace(s).

  If --ns is not specified, validate against all namespaces in the NWB file.

Validation against a namespace that is not cached within the schema is not currently possible but is a planned
feature.
