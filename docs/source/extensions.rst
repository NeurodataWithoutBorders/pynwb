.. _extending-nwb:

Extending NWB
=============

The following page will discuss how to extend NWB using PyNWB.

.. note::

    A simple example demonstrating the creation and use of a custom extension is available as part of the
    tutorial :ref:`tutorial-extending-nwb`.

.. _creating-extensions:

Creating new extensions
-----------------------

The NWB specification is designed to be extended to allow support for new and specialized data types that are not
supported in the core NWB specification.

The `Neurodata Extensions Catalog <https://nwb-extensions.github.io/>`_ provides a user-friendly template
for creating a new NWB extension: https://github.com/nwb-extensions/ndx-template . Users new to creating extensions
should start by following the instructions on the `ndx-template <https://github.com/nwb-extensions/ndx-template>`_
repo README. After the extension folder structure has been generated, use the PyNWB API to define new data types
within ``my_new_extension/src/spec/create_extension_spec.py``.

.. note::

    A recorded presentation of how NWB extensions and the Neurodata Extensions Catalog work can be viewed here:
    https://www.youtube.com/watch?v=_lvpY4PajS8

Defining new data types using PyNWB
-----------------------------------

Extension of the NWB format can be done using the classes :py:class:`~pynwb.spec.NWBGroupSpec`,
:py:class:`~pynwb.spec.NWBDatasetSpec`, :py:class:`~pynwb.spec.NWBAttributeSpec`,
and :py:class:`~pynwb.spec.NWBLinkSpec`, provided in the :py:mod:`pynwb.spec` module. See the API documentation
for these classes for detailed information on what information is required and optional for defining a new group,
dataset, attribute, or link.

* :py:class:`NWBGroupSpec documentation <pynwb.spec.NWBGroupSpec>`
* :py:class:`NWBDatasetSpec documentation <pynwb.spec.NWBDatasetSpec>`
* :py:class:`NWBAttributeSpec documentation <pynwb.spec.NWBAttributeSpec>`
* :py:class:`NWBLinkSpec documentation <pynwb.spec.NWBLinkSpec>`

Specifying new attributes
^^^^^^^^^^^^^^^^^^^^^^^^^

Specifying attributes is done with :py:class:`~pynwb.spec.NWBAttributeSpec`.

.. code-block:: python

    from pynwb.spec import NWBAttributeSpec

    spec = NWBAttributeSpec(
        name='bar',
        doc='a value for bar',
        dtype='float'
    )

Specifying new datasets
^^^^^^^^^^^^^^^^^^^^^^^

Specifying datasets is done with :py:class:`~pynwb.spec.NWBDatasetSpec`.

.. code-block:: python

    from pynwb.spec import NWBDatasetSpec

    spec = NWBDatasetSpec(
        doc='A custom NWB type',
        name='qux',
        attributes=[...],
        shape=(None, None)
    )


Specifying row-based tables and compound data types
+++++++++++++++++++++++++++++++++++++++++++++++++++

Row-based tables (compound data types), which can also be thought as structs, can be specified by providing a list of
:py:class:`~pynwb.spec.NWBDtypeSpec` objects to the ``dtype`` argument of :py:class:`~pynwb.spec.NWBDatasetSpec`.

.. code-block:: python

    from pynwb.spec import NWBDatasetSpec, NWBDtypeSpec

    spec = NWBDatasetSpec(
        doc='A custom NWB type',
        name='qux',
        attributes=[...],
        dtype=[
            NWBDtypeSpec(name='foo', doc='column for foo', dtype='int'),
            NWBDtypeSpec(name='bar', doc='a column for bar', dtype='float')
        ]
    )

Specifying groups
^^^^^^^^^^^^^^^^^

Specifying groups is done with the :py:class:`~pynwb.spec.NWBGroupSpec` class.

.. code-block:: python

    from pynwb.spec import NWBGroupSpec

    spec = NWBGroupSpec(
        doc='A custom NWB type',
        name='quux',
        attributes=[...],
        datasets=[...],
        groups=[...],
        links=[...]
    )


Specifying new neurodata types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

:py:class:`~pynwb.spec.NWBGroupSpec` and :py:class:`~pynwb.spec.NWBDatasetSpec` use the arguments
``neurodata_type_inc`` and ``neurodata_type_def`` for declaring new types and extending existing types. New types are
specified by setting the argument ``neurodata_type_def``. New types can extend an existing type
by specifying the argument ``neurodata_type_inc``. For more information on how these arguments work, see the
NWB schema language documentation:
https://schema-language.readthedocs.io/en/latest/specification_language_description.html#neurodata-type-def-and-neurodata-type-inc

Create a new type
+++++++++++++++++

.. code-block:: python

    # A list of NWBAttributeSpec objects to specify new attributes
    addl_attributes = [...]

    # A list of NWBDatasetSpec objects to specify new datasets
    addl_datasets = [...]

    # A list of NWBDatasetSpec objects to specify new groups
    addl_groups = [...]

    # list of NWBLinkSpec objects to specify additional groups or groups to be overridden
    addl_links = [...]

    spec = NWBGroupSpec(
        doc='A custom NWB type',
        neurodata_type_def='MyNewNWBType',
        attributes=addl_attributes,
        datasets=addl_datasets,
        groups=addl_groups,
        links=addl_links
    )

Extend an existing type
+++++++++++++++++++++++

.. code-block:: python

    spec = NWBGroupSpec(
        doc='An extended TimeSeries type',
        neurodata_type_def='MyExtendedTimeSeries',
        neurodata_type_inc='TimeSeries',
        attributes=addl_attributes,
        datasets=addl_datasets,
        groups=addl_groups,
        links=addl_links
    )

Existing types can be instantiated by specifying ``neurodata_type_inc`` alone.

.. code-block:: python

    # use another NWBGroupSpec object to specify that a group of type
    # ElectricalSeries should be present in the new type defined below
    addl_groups = [
        NWBGroupSpec(
            doc='An included ElectricalSeries instance',
            neurodata_type_inc='ElectricalSeries'
        )
    ]

    spec = NWBGroupSpec(
        doc='An extended TimeSeries type',
        neurodata_type_def='MyExtendedTimeSeries',
        neurodata_type_inc='TimeSeries',
        groups=addl_groups
    )


Datasets can be extended in the same manner using the keyword arguments `neurodata_type_inc` and `neurodata_type_def`
with the class :py:class:`~pynwb.spec.NWBDatasetSpec`.

Specifying new links
^^^^^^^^^^^^^^^^^^^^

Specifying links is done with the :py:class:`~pynwb.spec.NWBLinkSpec` class.

.. code-block:: python

    from pynwb.spec import NWBLinkSpec

    spec = NWBLinkSpec(
        doc='A custom link',
        name='my_link',
        target_type='MyExtendedTimeSeries'
    )


.. _saving-extensions:

Saving extensions
-----------------

Extensions are used by including them in a loaded namespace. Namespaces and extensions need to be saved to file
for downstream use. The class :py:class:`~pynwb.spec.NWBNamespaceBuilder` can be used to create new namespace and
specification files.

.. note::

    When using :py:class:`~pynwb.spec.NWBNamespaceBuilder`, the core NWB namespace is automatically included.

Create a new namespace with extensions
++++++++++++++++++++++++++++++++++++++

.. code-block:: python

    from pynwb.spec import NWBGroupSpec, NWBNamespaceBuilder, export_spec

    # create a builder for the namespace
    ns_builder = NWBNamespaceBuilder(
        doc="Extension for use in my laboratory",
        name="ndx-mylab",
        version='0.1.0',
        ...
    )

    # create extensions
    ext_timeseries_spec = NWBGroupSpec(
        doc='A custom TimeSeries',
        neurodata_type_def='MyExtendedTimeSeries',
        neurodata_type_inc='TimeSeries',
        attributes=[...],
        datasets=[...],
        groups=[...],
        links=[...]
    )

    ext_device_spec = NWBGroupSpec(
        doc='A custom Device',
        neurodata_type_def='MyExtendedDevice',
        neurodata_type_inc='Device',
        attributes=[...],
        datasets=[...],
        groups=[...],
        links=[...]
    )

    new_data_types = [ext_timeseries_spec, ext_device_spec]
    export_spec(ns_builder=ns_builder, new_data_types=new_data_types, output_dir='.')

.. tip::

    Using the API to generate extensions (rather than writing YAML sources directly) helps avoid errors in the
    specification (e.g., due to missing required keys or invalid values) and ensure compliance of the extension
    definition with the NWB specification language. It also helps with maintenance of extensions, e.g., if extensions
    have to be ported to newer versions of the
    `specification language <https://schema-language.readthedocs.io/en/latest/>`_ in the future.


.. _incorporating-extensions:

Incorporating extensions
------------------------

The NWB file format supports extending existing data types (See :ref:`extending-nwb` for more details on creating
extensions). Extensions must be registered with PyNWB to be used for reading and writing of custom neurodata types.

The following code demonstrates how to load namespaces from a given namespace file.

.. code-block:: python

    from pynwb import load_namespaces

    namespace_path = 'my_namespace.yaml'
    load_namespaces(namespace_path)

.. note::

    This will register all namespaces defined in the file ``'my_namespace.yaml'``.

NWBContainer : Representing custom data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To read and write custom data, corresponding :py:class:`~pynwb.core.NWBContainer` classes must be associated with their
respective specifications.
:py:class:`~pynwb.core.NWBContainer` classes are associated with their respective specification using the decorator
:py:func:`~pynwb.register_class`.

The following code demonstrates how to associate a specification with the :py:class:`~pynwb.core.NWBContainer` class
that represents it.

.. code-block:: python

    from pynwb import register_class

    @register_class('MyExtension', 'my_namespace')
    class MyExtensionContainer(NWBContainer):
        ...

:py:func:`~pynwb.register_class` can also be used as a function.

.. code-block:: python

    from pynwb import register_class

    class MyExtensionContainer(NWBContainer):
        ...

    register_class('my_namespace', 'MyExtension', MyExtensionContainer)

If you do not have an :py:class:`~pynwb.core.NWBContainer` subclass to associate with your extension specification,
a dynamically created class is created by default.

To use the dynamic class, you will need to retrieve the class object using the function :py:func:`~pynwb.get_class`.
Once you have retrieved the class object, you can use it just like you would a statically defined class.

.. code-block:: python

    from pynwb import get_class

    MyExtensionContainer = get_class('my_namespace', 'MyExtension')
    my_ext_inst = MyExtensionContainer(...)


If using IPython / Jupyter, you can access documentation for the class's constructor using the ``help`` command.

ObjectMapper : Customizing the mapping between NWBContainer and the Spec
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If your :py:class:`~pynwb.core.NWBContainer` extension requires custom mapping of the
:py:class:`~pynwb.core.NWBContainer`
class for reading and writing, you will need to implement and register a custom
:py:class:`~hdmf.build.objectmapper.ObjectMapper`.

:py:class:`~hdmf.build.objectmapper.ObjectMapper` extensions are registered with the decorator
:py:func:`~pynwb.register_map`.

.. code-block:: python

    from pynwb import register_map
    from hdmf.build import ObjectMapper

    @register_map(MyExtensionContainer)
    class MyExtensionMapper(ObjectMapper)
        ...

:py:func:`~pynwb.register_map` can also be used as a function.

.. code-block:: python

    from pynwb import register_map
    from hdmf.build import ObjectMapper

    class MyExtensionMapper(ObjectMapper)
        ...

    register_map(MyExtensionContainer, MyExtensionMapper)

.. tip::

    ``ObjectMapper`` instances allow you to customize how objects in the spec are mapped to attributes of your
    ``NWBContainer`` in PyNWB. This is useful, e.g., in cases where you want to customize the default mapping.
    For example, in ``TimeSeries``, the attribute ``unit`` which is defined on the dataset ``data``
    (i.e., ``data.unit``) would by default be mapped to the attribute ``data__unit`` on
    :py:class:`~pynwb.base.TimeSeries`. The ``ObjectMapper`` :py:class:`~pynwb.io.base.TimeSeriesMap` then changes
    this mapping to map ``data.unit`` to the attribute ``unit`` on :py:class:`~pynwb.base.TimeSeries` .
    ``ObjectMapper`` instances also allow you to customize how constructor arguments for your ``NWBContainer`` are
    constructed. E.g., in ``TimeSeries`` instead of explicit ``timestamps``, we may only have a ``starting_time``
    and ``rate``. In the ``ObjectMapper``, we could then construct ``timestamps`` from this data on data load to
    always have ``timestamps`` available for the user. For an overview of the concepts of containers, spec, builders,
    object mappers in PyNWB, see also :ref:`software-architecture`


.. _documenting-extensions:

Documenting extensions
----------------------

When using the recommended `ndx-template <https://github.com/nwb-extensions/ndx-template>`_ to create your extension,
follow the instructions in ``README.md`` and the generated ``NEXTSTEPS.md`` to document the extension.

Further reading
---------------

* **Using Extensions:** See :ref:`tutorial-extending-nwb` for an example on how to use extensions during read and write.
* **Specification Language:** For a detailed overview of the specification language itself, see
https://schema-language.readthedocs.io/en/latest/
