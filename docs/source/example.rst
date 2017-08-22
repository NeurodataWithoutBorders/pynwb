.. _examples:

Examples
===========

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here.

.. code-block:: python

    import numpy as np
    import scipy.stats as sps

    electrode_name = 'tetrode1'
    rate = 10.0
    np.random.seed(1234)
    ephys_data = np.random.rand(data_len)
    ephys_timestamps = np.arange(data_len) / rate
    spatial_timestamps = ephys_timestamps[::10]
    spatial_data = np.cumsum(sps.norm.rvs(size=(2,len(spatial_timestamps))), axis=-1).T

Creating and Writing NWB files
-----------------------------------------------------

When creating an NWB file, the first step is to create the :py:class:`~pynwb.file.NWBFile`. The first
argument is the name of the NWB file, and the second argument is a brief description of the dataset.

.. code-block:: python

    from datetime import datetime
    from pynwb import NWBFile

    f = NWBFile(filename, 'my first synthetic recording', 'EXAMPLE_ID', datetime.now(),
                experimenter='Dr. Bilbo Baggins',
                lab='Bag End Labatory',
                institution='University of Middle Earth at the Shire',
                experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
                session_id='LONELYMTN')

Once you have created your NWB and added all of your data and other necessary metadata, you can write it to disk using
the :py:class:`~form.backends.hdf5.h5tools.HDF5IO` class.

.. code-block:: python

    from form.backends.hdf5 import HDF5IO
    from pynwb import get_build_manager

    manager = get_build_manager()
    io = HDF5IO(filename, manager, mode='w')
    io.write(f)
    io.close()


Creating Epochs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Experimental epochs are represented with :py:class:`~pynwb.epoch.Epoch` objects. To create epochs for an NWB file,
you can use the :py:class:`~pynwb.file.NWBFile` instance method :py:meth:`~pynwb.file.NWBFile.create_epoch`.

.. code-block:: python

    epoch_tags = ('example_epoch',)
    ep1 = f.create_epoch('epoch1', timestamps[100], timestamps[200], tags=epoch_tags, description="the first test epoch")
    ep2 = f.create_epoch('epoch2', timestamps[600], timestamps[700], tags=epoch_tags, description="the second test epoch")


Creating Electrode Groups
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Electrode groups (i.e. experimentally relevant groupings of channels) are represented by :py:class:`~pynwb.ecephys.ElectrodeGroup` objects. To create
an electrode group, you can use the :py:class:`~pynwb.file.NWBFile` instance method :py:meth:`~pynwb.file.NWBFile.create_electrode_group`.

Before creating an :py:class:`~pynwb.ecephys.ElectrodeGroup`, you need to provide some information about the device that was used to record from the electrode.
This is done by creating a :py:class:`~pynwb.ecephys.Device` object using the instance method :py:meth:`~pynwb.file.NWBFile.create_device`.

.. code-block:: python

    device = f.create_device('trodes_rig123')


Once you have created the :py:class:`~pynwb.ecephys.Device`, you can create the :py:class:`~pynwb.ecephys.ElectrodeGroup`.

.. code-block:: python

    channel_description = ['channel1', 'channel2', 'channel3', 'channel4']
    num_channels = len(channel_description)
    channel_location = ['CA1'] * num_channels
    channel_filtering = ['no filtering'] * num_channels
    channel_coordinates = [(2.0,2.0,2.0)] * num_channels
    channel_impedance = [-1] * num_channels
    description = "an example tetrode"
    location = "somewhere in the hippocampus"

    electrode_group = f.create_electrode_group(electrode_name,
                                               channel_description,
                                               channel_location,
                                               channel_filtering,
                                               channel_coordinates,
                                               channel_impedance,
                                               description,
                                               location,
                                               device)



Creating TimeSeries
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TimeSeries objects can be created in two ways. The first way is by instantiating :ref:`timeseries_overview` objects directly and then adding them to
the :ref:`file_overview` using the instance method :py:func:`~pynwb.file.NWBFile.add_raw_timeseries`. The second way is by calling the :py:class:`~pynwb.file.NWBFile`
instance method :py:func:`~pynwb.file.NWBFile.create_timeseries`. This first example will demonstrate instatiating two different
types of :ref:`timeseries_overview` objects directly, and adding them with :py:meth:`~pynwb.file.NWBFile.add_raw_timeseries`.

.. code-block:: python

    from pynwb.ecephys import ElectricalSeries
    from pynwb.behavior import SpatialSeries

    ephys_ts = ElectricalSeries('test_ephys_data',
                                'test_source',
                                ephys_data,
                                electrode_group,
                                timestamps=ephys_timestamps,
                                # Alternatively, could specify starting_time and rate as follows
                                #starting_time=ephys_timestamps[0],
                                #rate=rate,
                                resolution=0.001,
                                comments="This data was randomly generated with numpy, using 1234 as the seed",
                                description="Random numbers generated with numpy.randon.rand")
    f.add_raw_timeseries(ephys_ts, [ep1, ep2])

    spatial_ts = SpatialSeries('test_spatial_timeseries',
                               'a stumbling rat',
                               spatial_data,
                               'origin on x,y-plane',
                               timestamps=spatial_timestamps,
                               resolution=0.1,
                               comments="This data was generated with numpy, using 1234 as the seed",
                               description="This 2D Brownian process generated with numpy.cumsum(scipy.stats.norm.rvs(size=(2,len(timestamps))), axis=-1).T")
    f.add_raw_timeseries(spatial_ts, [ep1, ep2])

.. _useextension:

Using Extensions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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

If your :py:class:`~pynwb.core.NWBContainer` extension requires custom mapping of the :py:class:`~pynwb.core.NWBContainer` class for reading and writing, you will need
to implement and register a custom :py:class:`~form.build.map.ObjectMapper`. :py:class:`~form.build.map.ObjectMapper` extensions are registerd with the decorator :py:func:`~pynwb.register_map`.

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


If you do not have an :py:class:`~pynwb.core.NWBContainer` subclass to associate with your extension specification, a dynamically created class is created by default.
To use the dynamic class, you will need to retrieve the class object using the function :py:func:`~pynwb.get_class`. Once you have retrieved the class object, you can
use it just like you would a statically defined class.

.. code-block:: python

    from pynwb import get_class
    MyExtensionContainer = get_class('my_namespace', 'MyExtension')
    my_ext_inst = MyExtensionContainer(...)


If using iPython, you can access documentation for the class's constructor using the help command.

.. _write_nwbfile:

Write an NWBFile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Writing NWB files to disk is handled by the :py:mod:`form` package, which :py:mod:`pynwb` depends. Currently, the only storage format supported by
:py:mod:`form` is HDF5. Reading and writing to and from HDF5 is handled by the class :py:class:`~form.backends.hdf5.h5tools.HDF5IO`. The first argument to this
is the path of the HDF5, and the second is the :py:class:`~form.build.map.BuildManager` to use for IO. Briefly, the :py:class:`~form.build.map.BuildManager` is a class
that manages objects to be read and written from disk. A PyNWB-specific BuildManager can be retrieved using the module-level function :py:func:`~pynwb.get_build_manager`.

.. code-block:: python

    from pynwb import NWBFile, get_build_manager
    from form.backends.hdf5 import HDF5IO

    # make an NWBFile
    start_time = datetime(1970, 1, 1, 12, 0, 0)
    create_date = datetime(2017, 4, 15, 12, 0, 0)
    nwbfile = NWBFile('test.nwb', 'a test NWB File', 'TEST123', start_time, file_create_date=create_date)
    ts = TimeSeries('test_timeseries', 'example_source', list(range(100,200,10)), 'SIunit', timestamps=list(range(10)), resolution=0.1)
    nwbfile.add_raw_timeseries(ts)

    manager = get_build_manager()
    path = "test_pynwb_io_hdf5.h5"

    io = HDF5IO(path, manager, mode='w')
    io.write(nwbfile)
    io.close()

The third argument to the :py:class:`~form.backends.hdf5.h5tools.HDF5IO` constructor is the mode for opening the HDF5 file. Valid modes are:

    ========  ================================================
     r        Readonly, file must exist
     r+       Read/write, file must exist
     w        Create file, truncate if exists
     w- or x  Create file, fail if exists
     a        Read/write if exists, create otherwise (default)
    ========  ================================================

.. _extending-nwb:

Extending NWB
-----------------------------------------------------

Creating new Extensions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The NWB specification is designed to be extended. Extension for the NWB format can be done so using classes provided in the :py:mod:`pynwb.spec` module.
The classes :py:class:`~pynwb.spec.NWBGroupSpec`, :py:class:`~pynwb.spec.NWBDatasetSpec`, :py:class:`~pynwb.spec.NWBAttributeSpec`, and :py:class:`~pynwb.spec.NWBLinkSpec`
can be used to define custom types.

:py:class:`~pynwb.spec.NWBGroupSpec` and :py:class:`~pynwb.spec.NWBDatasetSpec` use the arguments `neurodata_type_inc` and `neurodata_type_def` for
declaring new types and extending existing types. New types are specified by setting the argument `neurodata_type_def`. New types can extend an existing type
by specifying the argument `neurodata_type_inc`. Specifications can instantiate existing types by only specifying the `neurodata_type_inc`.

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

Use an existing type

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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
    newer versions of the `specification language <http://schema-language.readthedocs.io/en/latest/>`_
    in the future.


Documenting Extensions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using the same tools used to generate the documentation for the `NWB-N core format <http://nwb-schema.readthedocs.io/en/latest/>`_
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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* **Using Extensions:** See :ref:`useextension` for an example on how to use extensions during read and write.
* **Specification Language:** For a detailed overview of the specification language itself see http://schema-language.readthedocs.io/en/latest/

