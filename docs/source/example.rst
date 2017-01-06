.. _examples:

Examples
===========

The following examples will reference variables that may not be defined within the block they are used. For 
clarity, we define them here.

.. code-block:: python

    electrode_name = 'electrode1'
    description = "This is a test TimeSeries dataset, and has no scientific value"
    comments = "After a long journey there and back again, the treasures have been returned to their rightful owners."
    rate = 10.0
    data = numpy.random.rand(data_len)
    timestamps = numpy.arange(data_len) / rate

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

    electrode_name = 'tetrode1'
    f.create_electrode_group(electrode_name, (2.0,2.0,2.0), 'a lonely probe', 'trodes_rig123', 'the most desolate of brain regions')

Creating TimeSeries
-----------------------------------------------------

TimeSeries objects can be created in two ways. The first way is by instantiating :ref:`timeseries_overview` objects directly and then adding them to
the :ref:`file_overview` using the instance method :py:func:`~pynwb.ui.file.NWBFile.add_raw_timeseries`. The second way is by calling the :py:class:`~pynwb.ui.file.NWBFile` 
instance method :py:func:`~pynwb.ui.file.NWBFile.create_timeseries`. This first example will demonstrate instatiating :ref:`timeseries_overview` objects
directly, and adding them with :py:func:`~pynwb.ui.file.NWBFile.add_raw_timeseries`.

.. code-block:: python

    ts = ElectricalSeries('test_timeseries',
                          [electrode_name],
                          'test_source',
                          data=data,  
                          timestamps=timestamps,
                          # Alternatively, could specify starting_time and rate as follows
                          #starting_time=timestamps[0],
                          #rate=rate,
                          resolution=0.01,
                          comments=comments,
                          description=description)
    f.add_raw_timeseries(ts, [ep1, ep2])

