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
- To define a new neurodata type that does not extend an existing type, use ``neurodata_type_def`` and not ``neurodata_type_inc``.
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
``doc`` is a required argument that describes the purpose of the neurodata type.

``name`` is an optional argument that indicates the name of the Group that is written to the file. If this argument
is omitted, users will be required to enter a ``name`` field when creating instances of this neurodata type in the API.
You also have the option of specifying ``default_name``, in which case this name will be used as the name of the group
if no other name is provided in the PyNWB API.

``attributes``, ``datasets``, ``groups``, and ``links`` are all optional arguments that take lists of the
corresponding ``NWBSpec`` classes.

``quantity`` indicates the number of instances of this group that are allowed. See options
`here <https://schema-language.readthedocs.io/en/latest/specification_language_description.html#quantity>`_.

.. note::
    If you specify ``name``, ``quantity`` cannot be ``'*'``, ``'+'``, or an integer greater that 1, because you cannot
    have more than one group of the same name in the same parent group.

``linkable`` indicates whether a reference to this object can be placed elsewhere in the NWB file.

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

``dtype`` defines the type of the data, which can be a basic or compound type. See a list of options
`here <https://schema-language.readthedocs.io/en/latest/specification_language_description.html#sec-dtype>`_.

``shape`` is a specification defining the allowable shapes for the dataset. See the shape specification
`here <https://schema-language.readthedocs.io/en/latest/specification_language_description.html#shape>`_. ``None`` is
mapped to ``null``. Is no shape is provided, it is assumed that the dataset is only a single element.

``dims`` provides labels for each dimension of ``shape``.

``default_value`` is also available.

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
defined in the ``attributes`` field of of a :py:class:`~pynwb.spec.NWBGroupSpec` or
:py:class:`~pynwb.spec.NWBDatasetSpec`. ``attributes`` takes a list of :py:class:`~pynwb.spec.NWBAttributeSpec` objects.

.. code-block:: python

    from pynwb.spec import NWBAttributeSpec

    spec = NWBAttributeSpec(
        name='bar',
        doc='a value for bar',
        dtype='float'
    )

:py:class:`~pynwb.spec.NWBAttributeSpec` has arguments very similar to :py:class:`~pynwb.spec.NWBDatasetSpec`, with
are a few differences: ``neurodata_type_def`` and ``neurodata_type_inc`` are not allowed. An attribute cannot be a
neurodata type. The only way to match an object with a spec is through the name of the attribute so ``name`` is
required. You cannot have multiple attributes objects in the same place that correspond to the same
:py:class:`~pynwb.spec.NWBAttributeSpec`, since these would have to have the same name. Therefore, instead of
specifying number of ``quantity``, you have a ``required`` field which takes a boolean value.

.. tip::
    Dataset or Attribute? It is often possible to store data as either a Dataset or an Attribute. Our best advice is
    to keep Attributes small, and if they are going to take any substantial amount of space, make it a Dataset.

Link Specifications
^^^^^^^^^^^^^^^^^^^

You can store an object in one place and reference that object in another without copying the object using a
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
