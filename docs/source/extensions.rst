.. _extending-nwb:

Extending NWB
=============

Neurophysiology is always changing as new technologies are developed. While the core NWB schema supports many of the
most common data types in neurophysiology, we need a way to accommodate new technologies and unique metadata needs.
Neurodata extensions (NDX) allow us to define new data types. These data types can extend core types, contain core
types, or can be entirely new. These extensions are formally defined with a collection of YAML files following
the `NWB Specification Language <https://schema-language.readthedocs.io/en/latest/index.html>`_.

.. toctree::
    :maxdepth: 2

    extensions/create_extension
    extensions/spec_api
    extensions/auto_api
    extensions/custom_api
    extensions/documenting
    extensions/publishing
    extensions/examples
