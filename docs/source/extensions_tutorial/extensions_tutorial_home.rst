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

    2_create_extension_spec_walkthrough
    3_spec_api
    4_auto_api
    5_custom_api
    6_documenting_extension
