.. _examples:

Examples
===========

The following examples will reference variables that may not be defined within the block they are used. For
clarity, we define them here.

.. code-block:: python

    electrode_name = 'tetrode1'
    rate = 10.0
    np.random.seed(1234)
    ephys_data = np.random.rand(data_len)
    ephys_timestamps = np.arange(data_len) / rate
    spatial_timestamps = ephys_timestamps[::10]
    spatial_data = np.cumsum(sps.norm.rvs(size=(2,len(spatial_timestamps))), axis=-1).T

Creating and Writing NWB files
-----------------------------------------------------

When creating an NWB file, the first step is to create the :py:class:`~pynwb.ui.file.NWBFile`. The first
argument is the name of the NWB file, and the second argument is a brief description of the dataset.

.. code-block:: python

    f = NWBFile('test.nwb', 'my first synthetic recording',
                experimenter='Dr. Bilbo Baggins',
                lab='Bag End Labatory',
                institution='University of Middle Earth at the Shire',
                experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
                session_id='LONELYMTN')

Once you have created your NWB and added all of your data and other necessary metadata, you can write it to disk using
the :py:class:`~pynwb.io.write.HDFWriter` class.

.. code-block:: python

    writer = HDF5Writer()
    writer.write(f, f.filename)

Creating Epochs
-----------------------------------------------------

Experimental epochs are represented with :py:class:`~pynwb.ui.epoch.Epoch` objects. To create epochs for an NWB file,
you can use the :py:class:`~pynwb.ui.file.NWBFile` instance method :py:func:`~pynwb.ui.file.NWBFile.create_epoch`.

.. code-block:: python

    epoch_tags = ('example_epoch',)
    ep1 = f.create_epoch('epoch1', timestamps[100], timestamps[200], tags=epoch_tags, description="the first test epoch")
    ep2 = f.create_epoch('epoch2', timestamps[600], timestamps[700], tags=epoch_tags, description="the second test epoch")

Creating Electrode Groups
-----------------------------------------------------

Electrode groups (i.e. experimentally relevant groupings of channels) are represented by :py:class:`~pynwb.ui.ephys.ElectrodeGroup` objects. To create
an electrode group, you can use the :py:class:`~pynwb.ui.file.NWBFile` instance method :py:func:`~pynwb.ui.file.NWBFile.create_electrode_group`.

.. code-block:: python

    f.create_electrode_group(electrode_name, (2.0,2.0,2.0), 'a lonely probe', 'trodes_rig123', 'the most desolate of brain regions')

Creating TimeSeries
-----------------------------------------------------

TimeSeries objects can be created in two ways. The first way is by instantiating :ref:`timeseries_overview` objects directly and then adding them to
the :ref:`file_overview` using the instance method :py:func:`~pynwb.ui.file.NWBFile.add_raw_timeseries`. The second way is by calling the :py:class:`~pynwb.ui.file.NWBFile`
instance method :py:func:`~pynwb.ui.file.NWBFile.create_timeseries`. This first example will demonstrate instatiating two different
types of :ref:`timeseries_overview` objects directly, and adding them with :py:func:`~pynwb.ui.file.NWBFile.add_raw_timeseries`.

.. code-block:: python

    ephys_ts = ElectricalSeries('test_timeseries',
                                'test_source',
                                ephys_data,
                                [electrode_name],
                                timestamps=ephys_timestamps,
                                # Alternatively, could specify starting_time and rate as follows
                                #starting_time=ephys_timestamps[0],
                                #rate=rate,
                                resolution=0.001,
                                comments="This data was randomly generated with numpy, using 1234 as the seed",
                                description="Random numbers generated with numpy.randon.rand")
    f.add_raw_timeseries(ts, [ep1, ep2])

    spatial_ts = SpatialSeries('test_spatial_timeseries',
                               'a stumbling rat',
                               spatial_data,
                               'origin on x,y-plane',
                               timestamps=spatial_timestamps,
                               resolution=0.1,
                               comments="This data was generated with numpy, using 1234 as the seed",
                               description="This 2D Brownian process generated with numpy.cumsum(scipy.stats.norm.rvs(size=(2,len(timestamps))), axis=-1).T")
    f.add_raw_timeseries(spatial_ts, [ep1, ep2])

Using Extensions
-----------------------------------------------------

The NWB file format supports extending existing data types (See <create_link> for more details on creating extensions).
Extensions must be registered with PyNWB to be used for reading and writing of custom neurodata types.

The following code demonstrates how to load custom namespaces.

.. code-block:: python

    from pynwb import load_namespaces
    namespace_path = 'my_namespace.yaml'
    load_namespaces(namespace_path)

*NOTE*: This will register all namespaces defined in the file ``'my_namespace.yaml'``.

To read and write custom data, corresponding NWBContainer classes must be associated with their respective specifications.
NWBContainer classes are associated with their respective specification using the :ref:`~pynwb.register_class` decorator.

The following code demonstrates how to associate a specification with the NWBContainer class that represents it.

.. code-block:: python

    from pynwb import register_class
    @register_class('my_namespace', 'MyExtension')
    class MyExtensionContainer(NWBContainer):
        ...

This is the same as the following:

.. code-block:: python

    from pynwb import register_class
    class MyExtensionContainer(NWBContainer):
        ...
    register_class('my_namespace', 'MyExtension', MyExtensionContainer)

Write an NWBFile
-----------------------------------------------------

.. code-block:: python

    from pynwb import NWBFile, HDF5IO
    nwbfile = NWBFile(...)
    io = HDF5IO(...)
    io.write(nwbfile)

