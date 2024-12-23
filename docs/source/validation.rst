.. _validating:

Validating NWB files
====================

.. note:: 
  
  The pynwb validation CLI checks for structural compliance of NWB files with the NWB schema. 
  It is recommended to use the `NWBInspector CLI <https://nwbinspector.readthedocs.io/en/dev/>`_ 
  for more comprehensive validation of both structural compliance with the NWB schema and 
  compliance of data with NWB best practices. The NWBInspector runs both PyNWB validation as 
  described here and additional data checks.


Validating NWB files is handled by a command-line tool available in :py:mod:`~pynwb`.
The validator can be invoked like so:

.. code-block:: bash

  pynwb-validate test.nwb

If the file contains no NWB extensions, then this command will validate the file ``test.nwb`` against the
*core* NWB specification. On success, the output will be:

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

  pynwb-validate -n ndx-my-extension test.nwb

To validate against the version of the **core** NWB specification that is included with the installed version of
PyNWB, use the ``--no-cached-namespace`` flag. This can be useful in validating files against newer or older versions
of the **core** NWB specification that are installed with newer or older versions of PyNWB.

.. code-block:: bash

  pynwb-validate --no-cached-namespace test.nwb

.. Last updated 8/13/2021
.. code-block:: text

  $pynwb-validate --help
  usage: pynwb-validate [-h] [-lns] [-n NS] [--json-output-path JSON_OUTPUT_PATH] [--no-cached-namespace] paths [paths ...]

  Validate an NWB file

  positional arguments:
    paths                 NWB file paths

  options:
    -h, --help            show this help message and exit
    -lns, --list-namespaces
                          List the available namespaces and exit.
    -n NS, --ns NS        the namespace to validate against
    --json-output-path JSON_OUTPUT_PATH
                          Write json output to this location.
    --no-cached-namespace
                          Use the namespaces installed by PyNWB (true) or use the cached namespaces (false; default).

  If --ns is not specified, validate against all namespaces in the NWB file.

Validation against a namespace that is not cached within the schema is not currently possible but is a planned
feature.
