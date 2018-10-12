.. _validating:

Validating NWB files
====================

Validating NWB files is handled by a command-line tool available in :py:mod:`~pynwb`. The validator can be invoked like so:

.. code-block:: bash

    python -m pynwb.validate test.nwb

This will validate the file ``test.nwb`` against the *core* NWB specification. Validating against other specifications i.e. extensions
can be done using the ``-p`` and ``-n`` flags. For example, the following command will validate against the specifications referenced in the namespace
file ``mylab.namespace.yaml`` in addition to the core specification.

.. code-block:: bash

    python -m pynwb.validate -p mylab.namespace.yaml test.nwb

