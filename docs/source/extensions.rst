.. _extending-nwb:

Extending NWB
=============

Neurophysiology is always changing as new technologies are developed. While the core NWB schema supports many of the
most common data types in neurophysiology, we need a way to accommodate new technologies and unique metadata needs.
Neurodata extensions (NDX) allow us to  define new data types. These data types can extend core types, contain core
types, or can be entirely new. These extensions are formally defined with a collection of YAML files as defined by
the `NWB Specification Language <https://schema-language.readthedocs.io/en/latest/index.html>`_. Technically, you could
write these files on your own, but we have provided a more convenient API in the :py:mod:`~pynwb.spec` for creating
and managing extension.

Extensions should be created in their own repository, not alongside data conversion code. This facilitates sharing
and editing of the extension separately from the code that uses it. When starting a new extension, we highly
recommend using the `ndx-template <https://github.com/nwb-extensions/ndx-template>`_ repository, which automatically
generates a repository with the appropriate directory structure.

Structure of ``create_extension_spec.py``
-----------------------------------------

NWB organizes types into namespaces. You must define a new namespace before creating any new types. After following
the instructions from `ndx-template <https://github.com/nwb-extensions/ndx-template>`_, you should have a file
``ndx-my-ext/src/spec/create_extension_spec.py``. The beginning of this file should look like

.. code-block:: python

    from pynwb.spec import NWBNamespaceBuilder, export_spec, NWBGroupSpec, NWBAttributeSpec
    # TODO: import the following spec classes as needed
    # from pynwb.spec import NWBDatasetSpec, NWBLinkSpec, NWBDtypeSpec, NWBRefSpec


    def main():
        # these arguments were auto-generated from your cookiecutter inputs
        ns_builder = NWBNamespaceBuilder(
            doc="my description",
            name="ndx-my-ext",
            version="0.1.0",
            author="John Doe",
            contact="contact@gmail.com"
        )

Here, after the initial imports, we are defining meta-data of the extension.
Pay particular attention to ``version``. If you make changes to your extension
after the initial release, you should increase the numbers in your version
number, so that you can keep track of what exact version of the extension was
used for each file. We recommend using `semantic versioning <https://semver.org/>`_.

Next, we need to include types from the core schemas. This is analogous to
importing classes in Python. The generated file includes some example imports.

.. code-block:: python

    ns_builder.include_type('ElectricalSeries', namespace='core')
    ns_builder.include_type('TimeSeries', namespace='core')
    ns_builder.include_type('NWBDataInterface', namespace='core')
    ns_builder.include_type('NWBContainer', namespace='core')
    ns_builder.include_type('DynamicTableRegion', namespace='hdmf-common')
    ns_builder.include_type('VectorData', namespace='hdmf-common')
    ns_builder.include_type('Data', namespace='hdmf-common')

Neuroscience-specific data types are defined in the namespace ``'core'``
(which means core NWB). More general organizational data types that are not
specific to neuroscience and are relevant across scientific fields are defined
in ``'hdmf-common'``.

The generated ``create_extension_spec.py`` file next declares an example extension
for a new neurodata type called ``TetrodeSeries``. Then we creates a list of all
new data types.

.. code-block:: python

    tetrode_series = NWBGroupSpec(
        neurodata_type_def='TetrodeSeries',
        neurodata_type_inc='ElectricalSeries',
        doc=('An extension of ElectricalSeries to include the tetrode ID for '
             'each time series.'),
        attributes=[
            NWBAttributeSpec(
                name='trode_id',
                doc='The tetrode ID.',
                dtype='int32'
            )
        ],
    )

    # TODO: add all of your new data types to this list
    new_data_types = [tetrode_series]

The name of the new data type is declared in the ``neurodata_type_def`` arg. It is common for new data types to
extend from core types. Here, our new type extends ``ElectricalSeries`` by specifying
``neurodata_type_inc='ElectricalSeries'``. Since ``ElectricalSeries``
`is of Primitive Type Group <https://nwb-schema.readthedocs.io/en/latest/format.html?highlight=ElectricalSeries#electricalseries>`_,
our new type must be a ``NWBGroupSpec``. Most neurodata types are Groups, which act similarly to a directory or
folder within the NWB file. Next we define ``doc``, which is a required field that describes the purpose of the new
neurodata type. Next, ``TetrodeSeries`` adds the ``trode_id`` field to ``ElectricalSeries`` as an Attribute.

Below, we describe in more detail how to create custom neurodata types defined with
:py:class:`~pynwb.spec.NWBGroupSpec`, :py:class:`~pynwb.spec.NWBDatasetSpec`,
:py:class:`~pynwb.spec.NWBAttributeSpec`, and :py:class:`~pynwb.spec.NWBLinkSpec`.


Group Specifications
^^^^^^^^^^^^^^^^^^^^

Most neurodata types are Groups, which act like a directory or folder within the NWB file. A Group can have
within it Datasets, Attributes, Links, and/or other Groups. Groups are specified with the
:py:class:`~pynwb.spec.NWBGroupSpec` class, which provides a python API for defining
`NWB Group <https://schema-language.readthedocs.io/en/latest/specification_language_description.html#groups>`_ objects.

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
    group a neurodata type. If you do not need any of these features, and simply want to organize data within a
    neurodata type into an additional level of grouping, it may be OK to not define a neurodata type. The same goes
    for Datasets, but in our experience most of the time it makes sense *not* do define a neurodata type for datasets.

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


.. _saving-extensions:

Saving Extensions
-----------------

Extensions are used by including them in a loaded namespace. Namespaces and extensions need to be saved to file
for downstream use. The class :py:class:`~pynwb.spec.NWBNamespaceBuilder` can be used to create new namespace and
specification files.

.. note::

    When using :py:class:`~pynwb.spec.NWBNamespaceBuilder`, the core NWB namespace is automatically included

Create a new namespace with extensions

.. code-block:: python

    from pynwb.spec import NWBGroupSpec, NWBNamespaceBuilder

    # create a builder for the namespace
    ns_builder = NWBNamespaceBuilder("Extension for use in my laboratory", "mylab", version='0.1.0', ...)

    # create extensions
    ext1 = NWBGroupSpec('A custom SpikeEventSeries interface',
                        attributes=[...],
                        datasets=[...],
                        groups=[...],
                        neurodata_type_inc='SpikeEventSeries',
                        neurodata_type_def='MyExtendedSpikeEventSeries')

    ext2 = NWBGroupSpec('A custom EventDetection interface',
                        attributes=[...],
                        datasets=[...],
                        groups=[...],
                        neurodata_type_inc='EventDetection',
                        neurodata_type_def='MyExtendedEventDetection')


    # add the extension
    ext_source = 'mylab.specs.yaml'
    ns_builder.add_spec(ext_source, ext1)
    ns_builder.add_spec(ext_source, ext2)

    # include an existing namespace - this will include all specifications in that namespace
    ns_builder.include_namespace('collab_ns')

    # save the namespace and extensions
    ns_path = 'mylab.namespace.yaml'
    ns_builder.export(ns_path)


.. tip::

    Using the API to generate extensions (rather than writing YAML sources directly) helps avoid errors in the specification
    (e.g., due to missing required keys or invalid values) and ensure compliance of the extension definition with the
    NWB specification language. It also helps with maintenance of extensions, e.g., if extensions have to be ported to
    newer versions of the `specification language <https://schema-language.readthedocs.io/en/latest/>`_
    in the future.

.. _incorporating-extensions:

Incorporating extensions
------------------------

The NWB file format supports extending existing data types (See :ref:`extending-nwb` for more details on creating extensions).
Extensions must be registered with PyNWB to be used for reading and writing of custom neurodata types.

The following code demonstrates how to load custom namespaces.

.. code-block:: python

    from pynwb import load_namespaces
    namespace_path = 'my_namespace.yaml'
    load_namespaces(namespace_path)

.. note::

    This will register all namespaces defined in the file ``'my_namespace.yaml'``.

NWBContainer : Representing custom data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To read and write custom data, corresponding :py:class:`~pynwb.core.NWBContainer` classes must be associated with their respective specifications.
:py:class:`~pynwb.core.NWBContainer` classes are associated with their respective specification using the decorator :py:func:`~pynwb.register_class`.

The following code demonstrates how to associate a specification with the :py:class:`~pynwb.core.NWBContainer` class that represents it.

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


If using iPython, you can access documentation for the class's constructor using the help command.

ObjectMapper : Customizing the mapping between NWBContainer and the Spec
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

    ObjectMappers allow you to customize how objects in the spec are mapped to attributes of your NWBContainer in
    Python. This is useful, e.g., in cases where you want to customize the default mapping. For example in
    TimeSeries the attribute ``unit`` which is defined on the dataset ``data`` (i.e., ``data.unit``) would
    by default be mapped to the attribute ``data_unit`` on :py:class:`~pynwb.base.TimeSeries`. The ObjectMapper
    :py:class:`~pynwb.io.base.TimeSeriesMap` then changes this mapping to map ``data.unit`` to the attribute ``unit``
    on :py:class:`~pynwb.base.TimeSeries` . ObjectMappers also allow you to customize how constructor arguments
    for your ``NWBContainer`` are constructed. E.g., in TimeSeries instead of explicit ``timestamps`` we
    may only have a ``starting_time`` and ``rate``. In the ObjectMapper we could then construct ``timestamps``
    from this data on data load to always have ``timestamps`` available for the user.
    For an overview of the concepts of containers, spec, builders, object mappers in PyNWB see also
    :ref:`software-architecture`


.. _documenting-extensions:

Documenting Extensions
----------------------

Using the same tools used to generate the documentation for the `NWB-N core format <https://nwb-schema.readthedocs.io/en/latest/>`_
one can easily generate documentation in HTML, PDF, ePub and many other format for extensions as well.

Code to generate this documentation is maintained in a separate repo: https://github.com/hdmf-dev/hdmf-docutils. To use these utilities, install the package with pip:

.. code-block:: text

    pip install hdmf-docutils

For the purpose of this example, we assume that our current directory has the following structure.


.. code-block:: text

    - my_extension/
      - my_extension_source/
          - mylab.namespace.yaml
          - mylab.specs.yaml
          - ...
          - docs/  (Optional)
              - mylab_description.rst
              - mylab_release_notes.rst

In addition to Python 3.x, you will also need ``sphinx`` (including the ``sphinx-quickstart`` tool) installed.
Sphinx is available here http://www.sphinx-doc.org/en/stable/install.html .

We can now create the sources of our documentation as follows:

.. code-block:: text

    python3 nwb_init_sphinx_extension_doc  \
                 --project test \
                 --author "Dr. Master Expert" \
                 --version "1.2.3" \
                 --release alpha \
                 --output my_extension_docs \
                 --spec_dir my_extension_source \
                 --namespace_filename mylab.namespace.yaml \
                 --default_namespace mylab
                 --external_description my_extension_source/docs/mylab_description.rst \  (Optional)
                 --external_release_notes my_extension_source/docs/mylab_release_notes.rst \  (Optional)

To automatically generate the RST documentation files from the YAML (or JSON) sources of the extension simply run:

.. code-block:: text

    cd my_extension_docs
    make apidoc

Finally, to generate the HTML version of the docs run:

.. code-block:: text

    make html

.. tip::

    Additional instructions for how to use and customize the extension documentations are also available
    in the ``Readme.md`` file that  ``init_sphinx_extension_doc.py`` automatically adds to the docs.

.. tip::

    See ``make help`` for a list of available options for building the documentation in many different
    output formats (e.g., PDF, ePub, LaTeX, etc.).

.. tip::

    See ``python3 init_sphinx_extension_doc.py --help`` for a complete list of option to customize the documentation
    directly during initialization.

.. tip::

    The above example included additional description and release note docs as part of the specification. These are
    included in the docs via ``.. include`` commands so that changes in those files are automatically picked up
    when rebuilding to docs. Alternatively, we can also add custom documentation directly to the docs.
    In this case the options ``--custom_description format_description.rst``
    and ``--custom_release_notes format_release_notes.rst`` of the ``init_sphinx_extension_doc.py`` script are useful
    to automatically generate the basic setup for those files so that one can easily start to add content directly
    without having to worry about the additional setup.


Further Reading
---------------

* **Specification Language:** For a detailed overview of the specification language itself see https://schema-language.readthedocs.io/en/latest/
