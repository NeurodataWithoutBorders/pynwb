The Spec API
------------

The `NWB Specification Language <https://schema-language.readthedocs.io/en/latest/index.html>`_ defines a structure for
data and metadata using Groups, Datasets, Attributes, and Links. These structures are mapped onto
:py:class:`~pynwb.spec.NWBGroupSpec`, :py:class:`~pynwb.spec.NWBDatasetSpec`,
:py:class:`~pynwb.spec.NWBAttributeSpec`, and :py:class:`~pynwb.spec.NWBLinkSpec`, respectively. Here, we describe in
detail each of these classes, and demonstrate how to use them to create custom neurodata types.

Group Specifications
^^^^^^^^^^^^^^^^^^^^

Most neurodata types are Groups, which act like a directory or folder within the NWB file. A Group can have
within it Datasets, Attributes, Links, and/or other Groups. Groups are specified with the
:py:class:`~pynwb.spec.NWBGroupSpec` class, which provides a python API for specifying the structure for an
`NWB Group <https://schema-language.readthedocs.io/en/latest/specification_language_description.html#groups>`_ .

.. code-block:: python

    from pynwb.spec import NWBGroupSpec

    spec = NWBGroupSpec(
        neurodata_type_def='MyType',
        neurodata_type_inc='NWBDataInterface',
        doc='A custom NWB type',
        name='quux',
        attributes=[...],
        datasets=[...],
        groups=[...],
        links=[...]
    )

``neurodata_type_def`` and ``neurodata_type_inc`` define the neurodata type with the following rules:

- ``neurodata_type_def`` declares the name of the neurodata type.
- ``neurodata_type_inc`` indicates what data type you are extending (Groups must extend Groups, and Datasets must extend Datasets).
- To define a new neurodata type that does not extend an existing type, use
  ``neurodata_type_inc=NWBContainer`` for a group or ``neurodata_type_inc=NWBData`` for a dataset.
  ``NWBContainer`` and ``NWBData`` are base types for NWB.
- To use a type that has already been defined, use ``neurodata_type_inc`` and not ``neurodata_type_def``.
- You can define a group that is not a neurodata type by omitting both ``neurodata_type_def`` and ``neurodata_type_inc``.

.. tip::
    Although you have the option not to, there are several advantages to defining new groups and neurodata types.
    Neurodata types can be reused in multiple places in the schema, and can be linked to, while groups that are not
    neurodata types cannot. You can also have multiple neurodata type groups of the same type in the same group,
    whereas groups that are not neurodata types are limited to 0 or 1. Most of the time, we would recommend making a
    group a neurodata type. It is also generally better to extend your neurodata type from an existing type. Look
    through the `NWB schema <https://nwb-schema.readthedocs.io/en/latest/>`_ to see if a core neurodata type would
    work as a base for your new type. If no existing type works, consider extending
    :py:class:`~pynwb.base.NWBDataInterface``, which allows you to add the object to a processing module.

.. tip::
     New neurodata types should always be declared at the top level of the schema rather than nesting type
     definitions. I.e., when creating a new neurodata type it should be placed at the top level of your schema
     and then included at the appropriate location via ``neurodata_type_inc``. This approach greatly simplifies
     management of types.

For more information about the options available when specifying a Group, see the
`API docs for NWBGroupSpec <https://pynwb.readthedocs.io/en/stable/pynwb.spec.html?highlight=NWBGroupSpec#pynwb.spec.NWBGroupSpec>`_.

Dataset Specifications
^^^^^^^^^^^^^^^^^^^^^^

All larger blocks of numeric or text data should be stored in Datasets. Specifying datasets is done with
:py:class:`~pynwb.spec.NWBDatasetSpec`.

.. code-block:: python

    from pynwb.spec import NWBDatasetSpec

    spec = NWBDatasetSpec(
        doc='A custom NWB type',
        name='qux',
        shape=(None, None),
        attributes=[...]
    )

``neurodata_type_def``, ``neurodata_type_inc``, ``doc``, ``name``, ``default_name``, ``linkable``, ``quantity``, and
``attributes`` all work the same as they do in :py:class:`~pynwb.spec.NWBGroupSpec`, described in the previous section.

``dtype`` defines the type of the data, which can be a basic type, compound type, or reference type.
See a list of `dtype options <https://schema-language.readthedocs.io/en/latest/description.html#dtype>`_
as part of the specification language docs. Basic types can be defined as string objects and more complex
types via :py:class:`~pynwb.spec.NWBDtypeSpec` and
`RefSpec <https://hdmf.readthedocs.io/en/latest/hdmf.spec.spec.html#hdmf.spec.spec.RefSpec>`_.


``shape`` is a specification defining the allowable shapes for the dataset. See the
`shape specification <https://schema-language.readthedocs.io/en/latest/specification_language_description.html#shape>`_
as part of the specification language docs. ``None`` is mapped to ``null``. Is no shape is provided, it is
assumed that the dataset is only a single element.

If the dataset is a single element (scalar) that represents meta-data, consider using an Attribute (see
below) to store the data more efficiently instead. However, note that a Dataset can have Attributes,
whereas an Attribute cannot have Attributes of its own.
``dims`` provides labels for each dimension of ``shape``.

Using datasets to specify tables
++++++++++++++++++++++++++++++++

Row-based tables can be specified using :py:class:`~pynwb.spec.NWBDtypeSpec`. To specify a table, provide a
list of :py:class:`~pynwb.spec.NWBDtypeSpec` objects to the ``dtype`` argument.

.. code-block:: python

    from pynwb.spec import NWBDatasetSpec, NWBDtypeSpec

    spec = NWBDatasetSpec(
        doc='A custom NWB type',
        name='qux',
        attribute=[
            NWBAttributeSpec('baz', 'a value for baz', 'text'),
            ],
        dtype=[
            NWBDtypeSpec('foo', 'column for foo', 'int'),
            NWBDtypeSpec('bar', 'a column for bar', 'float')
            ]
        )

.. tip::
    Column-based tables are also possible and more flexible. See the documentation for `DynamicTable <https://hdmf.readthedocs.io/en/stable/tutorials/dynamictable.html>`_.

Attribute Specifications
^^^^^^^^^^^^^^^^^^^^^^^^

Attributes are small metadata objects describing the nature and/or intended usage of a Group or Dataset. Attributes are
defined in the ``attributes`` field of a :py:class:`~pynwb.spec.NWBGroupSpec` or
:py:class:`~pynwb.spec.NWBDatasetSpec`. ``attributes`` takes a list of :py:class:`~pynwb.spec.NWBAttributeSpec` objects.

.. code-block:: python

    from pynwb.spec import NWBAttributeSpec

    spec = NWBAttributeSpec(
        name='bar',
        doc='a value for bar',
        dtype='float'
    )

:py:class:`~pynwb.spec.NWBAttributeSpec` has arguments very similar to :py:class:`~pynwb.spec.NWBDatasetSpec`. A key difference is that an attribute cannot be a
neurodata type, i.e., the ``neurodata_type_def`` and ``neurodata_type_inc`` keys are not allowed. The only way to match an object with a spec is through the name of the attribute so ``name`` is
required. You cannot have multiple attributes on a single group/dataset that correspond to the same
:py:class:`~pynwb.spec.NWBAttributeSpec`, since these would have to have the same name. Therefore, instead of
specifying number of ``quantity``, you have a ``required`` field which takes a boolean value. Another
key difference between datasets and attributes is that attributes cannot have attributes of their own.

.. tip::
    Dataset or Attribute? It is often possible to store data as either a Dataset or an Attribute. Our best advice is
    to keep Attributes small.  In HDF5 the typical size limit for attributes is  64Kbytes. If an attribute is going to
    store more than 64Kbyte, then make it a Dataset. Attributes are also more efficient for storing very
    small data, such as scalars. However, attributes cannot have attributes of their own, and in HDF5,
    I/O filters, such as compression and chunking, cannot apply to attributes.


Link Specifications
^^^^^^^^^^^^^^^^^^^

You can store an object in one place and reference that object in another without copying the object using
`Links <https://schema-language.readthedocs.io/en/latest/specification_language_description.html#sec-link-spec>`_, which
can be defined using :py:class:`~pynwb.spec.NWBLinkSpec` objects.

.. code-block:: python

    from pynwb.spec import NWBLinkSpec

    spec = NWBLinkSpec(
        doc='my link',
        target_type='ElectricalSeries',
        quantity='?'
    )

``doc``, ``quantity``, and ``name`` work similarly to :py:class:`~pynwb.spec.NWBDatasetSpec`.

``target_type`` indicates the neurodata type that can be referenced.

.. tip::
   In case you need to store large collections of links, it can be more efficient to create a dataset for storing
   the links via object references. In NWB, this is used, e.g., in py:class:`~pynwb.epoch.TimeIntervals` to store
   collections of references to TimeSeries objects.

Using these functions in ``create_extension_spec.py`` and then running that file will generate YAML files that define
your extension. If you are a MATLAB user, you are now ready to switch over to MATLAB. Just run
``generateExtension ('path/to/ndx_name.extension.yaml')`` and the extension will be automatically generated for you. If
you are a Python user, you need to do a little more work to make a Python API that allows you to read and write data
according to this extension. The next two sections will teach you how to create this Python API.
