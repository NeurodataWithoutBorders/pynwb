Testing
-------

PyNWB has a goal of 100% test coverage, so it is important that any changes to the code base be covered by tests. Our
tests are split into three main categories, all of which are in the ``tests/`` folder:

* ``tests/back_compat`` tests to check compatibility of the API with older version of NWB. This is a collection of small NWB files with many different versions and a small testing script that ensures we can still read them.
* ``tests/unit``: tests that cover each use-case of each method or function
* ``tests/integration``: tests that neurodata types and NWB file can be written and read in various modes and
  backends including HDF5 and using the ros3 driver.

In addition to the ``tests/`` folder, there is also a :py:mod:`pynwb.testing` package. This module does not
contain any tests but instead contains classes and/or functions that can be used by PyNWB tests and can be imported
and used in the testing suite of any downstream library.

.. toctree::

    mock
    make_roundtrip_test