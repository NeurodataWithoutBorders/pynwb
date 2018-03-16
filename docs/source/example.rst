.. _examples:

Examples
========

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:

.. literalinclude:: ../code/creating-and-writing-nwbfile.py
   :language: python
   :start-after: prerequisites: start
   :end-before: prerequisites: end
   :dedent: 4


Creating and Writing NWB files
------------------------------

When creating a NWB file, the first step is to create the :py:class:`~pynwb.file.NWBFile`. The first
argument is the name of the NWB file, and the second argument is a brief description of the dataset.

.. literalinclude:: ../code/creating-and-writing-nwbfile.py
   :language: python
   :start-after: create-nwbfile: start
   :end-before: create-nwbfile: end
   :dedent: 4

Once you have created your NWB and added all of your data and other necessary metadata, you can write it to disk using
the :py:class:`~pynwb.form.backends.hdf5.h5tools.HDF5IO` class as a context:

.. literalinclude:: ../code/creating-and-writing-nwbfile.py
   :language: python
   :start-after: save-nwbfile: start
   :end-before: save-nwbfile: end
   :dedent: 4
   
or not:

.. literalinclude:: ../code/creating-and-writing-nwbfile.py
   :language: python
   :start-after: save-nwbfile2: start
   :end-before: save-nwbfile2: end
   :dedent: 4


Creating Epochs
^^^^^^^^^^^^^^^

Experimental epochs are represented with :py:class:`~pynwb.epoch.Epoch` objects. To create epochs for an NWB file,
you can use the :py:class:`~pynwb.file.NWBFile` instance method :py:meth:`~pynwb.file.NWBFile.create_epoch`.

.. literalinclude:: ../code/creating-and-writing-nwbfile.py
   :language: python
   :start-after: create-epochs: start
   :end-before: create-epochs: end
   :dedent: 4


Creating Electrode Groups
^^^^^^^^^^^^^^^^^^^^^^^^^

Electrode groups (i.e. experimentally relevant groupings of channels) are represented by :py:class:`~pynwb.ecephys.ElectrodeGroup` objects. To create
an electrode group, you can use the :py:class:`~pynwb.file.NWBFile` instance method :py:meth:`~pynwb.file.NWBFile.create_electrode_group`.

Before creating an :py:class:`~pynwb.ecephys.ElectrodeGroup`, you need to provide some information about the device that was used to record from the electrode.
This is done by creating a :py:class:`~pynwb.ecephys.Device` object using the instance method :py:meth:`~pynwb.file.NWBFile.create_device`.

.. literalinclude:: ../code/creating-and-writing-nwbfile.py
   :language: python
   :start-after: create-device: start
   :end-before: create-device: end
   :dedent: 4


Once you have created the :py:class:`~pynwb.ecephys.Device`, you can create the :py:class:`~pynwb.ecephys.ElectrodeGroup`.

.. literalinclude:: ../code/creating-and-writing-nwbfile.py
   :language: python
   :start-after: create-electrode-groups: start
   :end-before: create-electrode-groups: end
   :dedent: 4


Finally, you can then create the associated :py:class:`~pynwb.ecephys.ElectrodeTable` and :py:class:`~pynwb.ecephys.ElectrodeTableRegion`.

.. literalinclude:: ../code/creating-and-writing-nwbfile.py
   :language: python
   :start-after: create-electrode-table-region: start
   :end-before: create-electrode-table-region: end
   :dedent: 4


Creating TimeSeries
^^^^^^^^^^^^^^^^^^^

TimeSeries objects can be created by instantiating :ref:`timeseries_overview` objects directly and then adding them to
the :ref:`file_overview` using the instance method :py:func:`~pynwb.file.NWBFile.add_acquisition`.

This first example will demonstrate instantiating two different types of :ref:`timeseries_overview` objects directly,
and adding them with :py:meth:`~pynwb.file.NWBFile.add_acquisition`.

.. literalinclude:: ../code/creating-and-writing-nwbfile.py
   :language: python
   :start-after: create-timeseries: start
   :end-before: create-timeseries: end
   :dedent: 4

For additional :py:class:`~pynwb.base.TimeSeries` classes that can be added as acquisition, see the :ref:`TimeSeries overview <timeseries_overview>`.


Adding other acquisition data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Subclasses of :py:class:`~pynwb.core.NWBDataInterface` can also be added as acquisition data.

The follow example shows how to do this with two container types that hold :py:class:`~pynwb.base.TimeSeries`.

.. literalinclude:: ../code/creating-and-writing-nwbfile.py
   :language: python
   :start-after: create-data-interface: start
   :end-before: create-data-interface: end
   :dedent: 4

For additional :py:class:`~pynwb.core.NWBDataInterface` classes that can be added as acquisition, see the :ref:`ProcessingModules overview <modules_overview>`.

Adding other acquisition data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Subclasses of :py:class:`~pynwb.core.NWBDataInterface` can also be added as acquisition data.

The follow example shows how to do this with two container types that hold :py:class:`~pynwb.base.TimeSeries`.

.. literalinclude:: ../code/creating-and-writing-nwbfile.py
   :language: python
   :start-after: create-data-interface: start
   :end-before: create-data-interface: end
   :dedent: 4


.. _useextension:

Compressing datasets
^^^^^^^^^^^^^^^^^^^^

HDF5 allows for compression of dataset. This is controled on a per-dataset basis [#]_. To compress a dataset,
wrap the data object (e.g. a :py:class:`list` or :py:class:`~numpy.ndarray`) with :py:class:`~pynwb.form.backends.hdf5.h5_utils.H5DataIO`.

.. literalinclude:: ../code/creating-and-writing-nwbfile.py
   :language: python
   :start-after: create-compressed-timeseries: start
   :end-before: create-compressed-timeseries: end
   :dedent: 4

.. [#] Global compression of all datasets is not allowed for performance reasons.


Using Extensions
^^^^^^^^^^^^^^^^

The NWB file format supports extending existing data types (See :ref:`extending-nwb` for more details on creating extensions).
Extensions must be registered with PyNWB to be used for reading and writing of custom neurodata types.

The following code demonstrates how to load custom namespaces.

.. code-block:: python

    from pynwb import load_namespaces
    namespace_path = 'my_namespace.yaml'
    load_namespaces(namespace_path)

.. note::

    This will register all namespaces defined in the file ``'my_namespace.yaml'``.

To read and write custom data, corresponding :py:class:`~pynwb.core.NWBContainer` classes must be associated with their respective specifications.
:py:class:`~pynwb.core.NWBContainer` classes are associated with their respective specification using the decorator :py:func:`~pynwb.register_class`.

The following code demonstrates how to associate a specification with the :py:class:`~pynwb.core.NWBContainer` class that represents it.

.. code-block:: python

    from pynwb import register_class
    @register_class('my_namespace', 'MyExtension')
    class MyExtensionContainer(NWBContainer):
        ...

:py:func:`~pynwb.register_class` can also be used as a function.

.. code-block:: python

    from pynwb import register_class
    class MyExtensionContainer(NWBContainer):
        ...
    register_class('my_namespace', 'MyExtension', MyExtensionContainer)

If your :py:class:`~pynwb.core.NWBContainer` extension requires custom mapping of the :py:class:`~pynwb.core.NWBContainer`
class for reading and writing, you will need to implement and register a custom :py:class:`~pynwb.form.build.map.ObjectMapper`.

:py:class:`~pynwb.form.build.map.ObjectMapper` extensions are registered with the decorator :py:func:`~pynwb.register_map`.

.. code-block:: python

    from pynwb import register_map
    from form import ObjectMapper
    @register_map(MyExtensionContainer)
    class MyExtensionMapper(ObjectMapper)
        ...

:py:func:`~pynwb.register_map` can also be used as a function.

.. code-block:: python

    from pynwb import register_map
    from form import ObjectMapper
    class MyExtensionMapper(ObjectMapper)
        ...
    register_map(MyExtensionContainer, MyExtensionMapper)


If you do not have an :py:class:`~pynwb.core.NWBContainer` subclass to associate with your extension specification,
a dynamically created class is created by default.

To use the dynamic class, you will need to retrieve the class object using the function :py:func:`~pynwb.get_class`.
Once you have retrieved the class object, you can use it just like you would a statically defined class.

.. code-block:: python

    from pynwb import get_class
    MyExtensionContainer = get_class('my_namespace', 'MyExtension')
    my_ext_inst = MyExtensionContainer(...)


If using iPython, you can access documentation for the class's constructor using the help command.

.. _write_nwbfile:

Write an NWBFile
^^^^^^^^^^^^^^^^

Writing NWB files to disk is handled by the :py:mod:`pynwb.form` package. Currently,
the only storage format supported by :py:mod:`pynwb.form` is HDF5.

Reading and writing to and from HDF5 is handled by the class :py:class:`~pynwb.form.backends.hdf5.h5tools.HDF5IO`. The
only required argument to this is the path of the HDF5 file. A second, optional argument is the
:py:class:`~pynwb.form.build.map.BuildManager` to use for IO.

Briefly, the :py:class:`~pynwb.form.build.map.BuildManager` is a class that manages objects to be read and written
from disk. A PyNWB-specific BuildManager can be retrieved using the module-level function :py:func:`~pynwb.get_manager`.

Alternatively, the :py:class:`~pynwb.form.build.map.BuildManager` that a :py:class:`~pynwb.form.backends.io.FORMIO` used
can be retrieved from the :py:attr:`~pynwb.form.backends.io.FORMIO.manager` attribute.


.. literalinclude:: ../code/creating-and-writing-nwbfile-2.py
   :language: python
   :start-after: example: start
   :end-before: example: end
   :dedent: 4


.. note::
    All :py:class:`~pynwb.form.backends.io.FORMIO` objects are context managers.


The third argument to the :py:class:`~pynwb.form.backends.hdf5.h5tools.HDF5IO` constructor is the mode for opening the HDF5 file. Valid modes are:

    ========  ================================================
     r        Readonly, file must exist
     r+       Read/write, file must exist
     w        Create file, truncate if exists
     w- or x  Create file, fail if exists
     a        Read/write if exists, create otherwise (default)
    ========  ================================================

.. _extending-nwb:

Extending NWB
-------------

Creating new Extensions
^^^^^^^^^^^^^^^^^^^^^^^

The NWB specification is designed to be extended. Extension for the NWB format can be done so using classes provided in the :py:mod:`pynwb.spec` module.
The classes :py:class:`~pynwb.spec.NWBGroupSpec`, :py:class:`~pynwb.spec.NWBDatasetSpec`, :py:class:`~pynwb.spec.NWBAttributeSpec`, and :py:class:`~pynwb.spec.NWBLinkSpec`
can be used to define custom types.

Attribute Specifications
________________________

Specifying attributes is done with :py:class:`~pynwb.spec.NWBAttributeSpec`.

.. code-block:: python

    from pynwb.spec import NWBAttributeSpec

    spec = NWBAttributeSpec('bar', 'float', 'a value for bar')

Dataset Specifications
______________________

Specifying datasets is done with :py:class:`~pynwb.spec.NWBDatasetSpec`.

.. code-block:: python

    from pynwb.spec import NWBDatasetSpec

    spec = NWBDatasetSpec('A custom NWB type',
                        attribute=[
                            NWBAttributeSpec('baz', 'str', 'a value for baz'),
                        ],
                        shape=(None, None))


Using datasets to specify tables
++++++++++++++++++++++++++++++++

Tables can be specified using :py:class:`~pynwb.spec.NWBDtypeSpec`. To specify a table, provide a
list of :py:class:`~pynwb.spec.NWBDtypeSpec` objects to the *dtype* argument.

.. code-block:: python

    from pynwb.spec import NWBDatasetSpec, NWBDtypeSpec

    spec = NWBDatasetSpec('A custom NWB type',
                        attribute=[
                            NWBAttributeSpec('baz', 'a value for baz', 'str'),
                        ],
                        dtype=[
                            NWBDtypeSpec('foo', 'column for foo', 'int'),
                            NWBDtypeSpec('bar', 'a column for bar', 'float')
                        ])

Compound data types can be nested.

.. code-block:: python

    from pynwb.spec import NWBDatasetSpec, NWBDtypeSpec

    spec = NWBDatasetSpec('A custom NWB type',
                        attribute=[
                            NWBAttributeSpec('baz', 'a value for baz', 'str'),
                        ],
                        dtype=[
                            NWBDtypeSpec('foo', 'a column for foo', 'int'),
                            NWBDtypeSpec('bar', 'a column for bar', 'float')
                        ])

Group Specifications
____________________

Specifying groups is done with the :py:class:`~pynwb.spec.NWBGroupSpec` class.

.. code-block:: python

    from pynwb.spec import NWBGroupSpec

    # A list of NWBAttributeSpec objects to specify new attributes
    addl_attributes = [...]
    # A list of NWBDatasetSpec objects to specify new datasets
    addl_datasets = [...]
    # A list of NWBDatasetSpec objects to specify new groups
    addl_groups = [...]
    spec = NWBGroupSpec('A custom NWB type',
                        attributes = addl_attributes,
                        datasets = addl_datasets,
                        groups = addl_groups)

Neurodata Type Specifications
_____________________________

:py:class:`~pynwb.spec.NWBGroupSpec` and :py:class:`~pynwb.spec.NWBDatasetSpec` use the arguments `neurodata_type_inc` and `neurodata_type_def` for
declaring new types and extending existing types. New types are specified by setting the argument `neurodata_type_def`. New types can extend an existing type
by specifying the argument `neurodata_type_inc`.

Create a new type

.. code-block:: python

    from pynwb.spec import NWBGroupSpec

    # A list of NWBAttributeSpec objects to specify new attributes
    addl_attributes = [...]
    # A list of NWBDatasetSpec objects to specify new datasets
    addl_datasets = [...]
    # A list of NWBDatasetSpec objects to specify new groups
    addl_groups = [...]
    spec = NWBGroupSpec('A custom NWB type',
                        attributes = addl_attributes,
                        datasets = addl_datasets,
                        groups = addl_groups,
                        neurodata_type_def='MyNewNWBType')

Extend an existing type

.. code-block:: python

    from pynwb.spec import NWBGroupSpec

    # A list of NWBAttributeSpec objects to specify additional attributes or attributes to be overriden
    addl_attributes = [...]
    # A list of NWBDatasetSpec objects to specify additional datasets or datasets to be overriden
    addl_datasets = [...]
    # A list of NWBGroupSpec objects to specify additional groups or groups to be overriden
    addl_groups = [...]
    spec = NWBGroupSpec('An extended NWB type',
                        attributes = addl_attributes,
                        datasets = addl_datasets,
                        groups = addl_groups,
                        neurodata_type_inc='Clustering',
                        neurodata_type_def='MyExtendedClustering')

Existing types can be instantiate by specifying `neurodata_type_inc` alone.

.. code-block:: python

    from pynwb.spec import NWBGroupSpec

    # use another NWBGroupSpec object to specify that a group of type
    # ElectricalSeries should be present in the new type defined below
    addl_groups = [ NWBGroupSpec('An included ElectricalSeries instance',
                                 neurodata_type_inc='ElectricalSeries') ]

    spec = NWBGroupSpec('An extended NWB type',
                        groups = addl_groups,
                        neurodata_type_inc='Clustering',
                        neurodata_type_def='MyExtendedClustering')


Datasets can be extended in the same manner (with regard to `neurodata_type_inc` and `neurodata_type_def`,
by using the class :py:class:`~pynwb.spec.NWBDatasetSpec`.

Saving Extensions
^^^^^^^^^^^^^^^^^

Extensions are used by including them in a loaded namespace. Namespaces and extensions need to be saved to file
for downstream use. The class :py:class:`~pynwb.spec.NWBNamespaceBuilder` can be used to create new namespace and
specification files.

.. note::

    When using :py:class:`~pynwb.spec.NWBNamespaceBuilder`, the core NWB namespace is automatically included

Create a new namespace with extensions

.. code-block:: python

    from pynwb.spec import NWBGroupSpec, NWBNamespaceBuilder

    # create a builder for the namespace
    ns_builder = NWBNamespaceBuilder("Extension for use in my laboratory", "mylab", ...)

    # create extensions
    ext1 = NWBGroupSpec('A custom Clustering interface',
                        attributes = [...]
                        datasets = [...],
                        groups = [...],
                        neurodata_type_inc='Clustering',
                        neurodata_type_def='MyExtendedClustering')

    ext2 = NWBGroupSpec('A custom ClusterWaveforms interface',
                        attributes = [...]
                        datasets = [...],
                        groups = [...],
                        neurodata_type_inc='ClusterWaveforms',
                        neurodata_type_def='MyExtendedClusterWaveforms')


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
    NWB specification language. It also helps with maintanence of extensions, e.g., if extensions have to be ported to
    newer versions of the `specification language <https://schema-language.readthedocs.io/en/latest/>`_
    in the future.


Documenting Extensions
^^^^^^^^^^^^^^^^^^^^^^

Using the same tools used to generate the documentation for the `NWB-N core format <https://nwb-schema.readthedocs.io/en/latest/>`_
one can easily generate documentation in HTML, PDF, ePub and many other format for extensions as well.

For the purpose of this example we assume that our current directory has the following structure.

.. code-block:: text

    - nwb_schema (cloned from `https://github.com/NeurodataWithoutBorders/nwb-schema`)
    - my_extension/
        - my_extension_source/
            - mylab.namespace.yaml
            - mylab.specs.yaml
            - ...
            - docs/  (Optional)
                - mylab_description.rst
                - mylab_release_notes.rst

In addition to Python 3.x you will also need ``sphinx`` (including the ``sphinx-quickstart`` tool) installed.
Sphinx is availble here http://www.sphinx-doc.org/en/stable/install.html .

We can now create the sources of our documentation as follows:

.. code-block:: text

    python3 nwb-schema/docs/utils/init_sphinx_extension_doc.py \
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

The new folder ``my_extension_docs/`` now contains the basic setup for the documentation. To automatically generate
the RST documentation files from the YAML (or JSON) sources of the extension simply run:

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
^^^^^^^^^^^^^^^

* **Using Extensions:** See :ref:`useextension` for an example on how to use extensions during read and write.
* **Specification Language:** For a detailed overview of the specification language itself see https://schema-language.readthedocs.io/en/latest/

Validating NWB files
--------------------

Validating NWB files is handled by a command-line tool availble in :py:mod:`~pynwb`. The validator can be invoked like so:

.. code-block:: bash

    python -m pynwb.validate test.nwb

This will validate the file ``test.nwb`` against the *core* NWB specification. Validating against other specifications i.e. extensions
can be done using the ``-p`` and ``-n`` flags. For example, the following command will validate against the specifications referenced in the namespace
file ``mylab.namespace.yaml`` in addition to the core specification.

.. code-block:: bash

    python -m pynwb.validate -p mylab.namespace.yaml test.nwb

