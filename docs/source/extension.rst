.. _extensions_tutorial:

Extending NWB
==============

The NWB-N format was designed to be easily extendable. Here we will demonstrate how to extend NWB using the
PyNWB API.

Defining extensions
-----------------------------------------------------

Extensions should be defined separately from the code that uses the extensions. This design decision is based on the assumption that
extension will be written once, and read or used multiple times. Here, we provide an example of how to create an extension for subsequent use.
(For more information on the available tools for creating extensions, see :ref:`extending-nwb`).


The following block of code demonstrates how to create a new namespace, and then add a new `neurodata_type` to this namespace. Finally,
it calls :py:meth:`pynwb.spec.NWBNamespaceBuilder.export` to save the extensions to disk for downstream use.

.. code-block:: python

    from pynwb import NWBNamespaceBuilder, NWBGroupSpec, NWBAttributeSpec

    ns_path = "mylab.namespace.yaml"
    ext_source = "mylab.extensions.yaml"

    ns_builder = NWBNamespaceBuilder('Extension for us in my Lab', "mylab")
    ext = NWBGroupSpec('A custom ElectricalSeries for my lab',
                       attributes=[NWBAttributeSpec('trode_id', 'int', 'the tetrode id')],
                       neurodata_type_inc='ElectricalSeries',
                       neurodata_type_def='TetrodeSeries')

    ns_builder.add_spec(ext_source, ext)
    ns_builder.export(ns_path)

Running this block will produce two files. The first file shown below is the

The first file is the namespace file.
.. code-block:: yaml

    # mylab.namespace.yaml
    namespaces:
    - doc: Extension for us in my Lab
      name: mylab
      schema:
      - namespace: core
      - source: fake_extension.yaml

And the second file is the file containing the details on new types.
.. code-block:: yaml

    # mylab.extensions.yaml
    groups:
    - attributes:
      - doc: the tetrode id
        dtype: int
        name: trode_id
      doc: A custom ElectricalSeries for my lab
      neurodata_type_def: TetrodeSeries
      neurodata_type_inc: ElectricalSeries





:ref:`useextension`

