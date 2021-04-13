Creating an NDX repository
---------------------------

Extensions should be created in their own repository, not alongside data conversion code. This facilitates sharing
and editing of the extension separately from the code that uses it. When starting a new extension, we highly
recommend using the `ndx-template <https://github.com/nwb-extensions/ndx-template>`_ repository, which automatically
generates a repository with the appropriate directory structure.

After you finish the instructions `here <https://github.com/nwb-extensions/ndx-template#getting-started>`_,
you should have a directory structure that looks like this

.. code-block::

    ├── LICENSE.txt
    ├── MANIFEST.in
    ├── NEXTSTEPS.md
    ├── README.md
    ├── docs
    │   ├── Makefile
    │   ├── README.md
    │   ├── make.bat
    │   └── source
    │       ├── _static
    │       │   └── theme_overrides.css
    │       ├── conf.py
    │       ├── conf_doc_autogen.py
    │       ├── credits.rst
    │       ├── description.rst
    │       ├── format.rst
    │       ├── index.rst
    │       └── release_notes.rst
    ├── requirements.txt
    ├── setup.cfg
    ├── setup.py
    ├── spec
    │   ├── ndx-example.extensions.yaml
    │   └── ndx-example.namespace.yaml
    └── src
        ├── matnwb
        │   └── README.md
        ├── pynwb
        │   ├── README.md
        │   ├── ndx_example
        │   │   └── __init__.py
        │   └── tests
        │       ├── __init__.py
        │       └── test_tetrodeseries.py
        └── spec
            └── create_extension_spec.py