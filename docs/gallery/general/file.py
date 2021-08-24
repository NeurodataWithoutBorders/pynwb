"""
.. _basics:

NWB File Basics
===============

This example will focus on the basics of working with an :py:class:`~pynwb.file.NWBFile` object,
including writing and reading of an NWB file. Before we dive into code showing how to use an
:py:class:`~pynwb.file.NWBFile`, we first provide a brief overview of the basic concepts of NWB. If you
are already familiar with the concepts of :ref:`timeseries_overview` and :ref:`modules_overview`, then
feel free to skip the :ref:`basics_background` part and go directly to :ref:`basics_nwbfile`.

.. _basics_background:

Background: Basic concepts
--------------------------

In the `NWB Format <https://nwb-schema.readthedocs.io>`_, each experimental session is typically
represented by a separate NWB file. NWB files are represented in PyNWB by :py:class:`~pynwb.file.NWBFile`
objects which provide functionality for creating and retrieving:

 * :ref:`timeseries_overview` datasets, i.e., objects for storing time series data
 * :ref:`modules_overview`, i.e., objects for storing and grouping analyses, and
 * experimental metadata and other metadata related to data provenance.

The following sections describe the :py:class:`~pynwb.base.TimeSeries` and :py:class:`~pynwb.base.ProcessingModules`
classes in further detail.

.. _timeseries_overview:

TimeSeries
^^^^^^^^^^

:py:class:`~pynwb.base.TimeSeries` objects store time series data and correspond to the *TimeSeries* specifications
provided by the `NWB Format`_ . Like the NWB specification, :py:class:`~pynwb.base.TimeSeries` Python objects
follow an object-oriented inheritance pattern, i.e., the class :py:class:`~pynwb.base.TimeSeries`
serves as the base class for all other :py:class:`~pynwb.base.TimeSeries` types, such as,
:py:class:`~pynwb.ecephys.ElectricalSeries`, which itself may have further subtypes, e.g.,
:py:class:`~pynwb.ecephys.SpikeEventSeries`.

.. seealso::

    For your reference, NWB defines the following main :py:class:`~pynwb.base.TimeSeries` subtypes:

    * **Extracellular electrophysiology:**
      :py:class:`~pynwb.ecephys.ElectricalSeries`, :py:class:`~pynwb.ecephys.SpikeEventSeries`

    * **Intracellular electrophysiology:**
      :py:class:`~pynwb.icephys.PatchClampSeries` is the base type for all intracellular time series, which
      is further refined into subtypes depending on the type of recording:
      :py:class:`~pynwb.icephys.CurrentClampSeries`,
      :py:class:`~pynwb.icephys.IZeroClampSeries`,
      :py:class:`~pynwb.icephys.CurrentClampStimulusSeries`,
      :py:class:`~pynwb.icephys.VoltageClampSeries`,
      :py:class:`~pynwb.icephys.VoltageClampStimulusSeries`.

    * **Optical physiology and imaging:** :py:class:`~pynwb.image.ImageSeries` is the base type
      for image recordings and is further refined by the
      :py:class:`~pynwb.image.ImageMaskSeries`,
      :py:class:`~pynwb.image.OpticalSeries`, and
      :py:class:`~pynwb.ophys.TwoPhotonSeries` types.
      Other related time series types are:
      :py:class:`~pynwb.image.IndexSeries` and
      :py:class:`~pynwb.ophys.RoiResponseSeries`.

    * **Others** :py:class:`~pynwb.ogen.OptogeneticSeries`,
      :py:class:`~pynwb.behavior.SpatialSeries`,
      :py:class:`~pynwb.misc.DecompositionSeries`,
      :py:class:`~pynwb.misc.AnnotationSeries`,
      :py:class:`~pynwb.misc.AbstractFeatureSeries`, and
      :py:class:`~pynwb.misc.IntervalSeries`.


.. _modules_overview:

Processing Modules
^^^^^^^^^^^^^^^^^^

Processing modules are objects that group together common analyses done during processing of data.
Processing module objects are unique collections of analysis results. To standardize the storage of
common analyses, NWB provides the concept of an :py:class:`~pynwb.core.NWBDataInterface`, where the output of
common analyses are represented as objects that extend the :py:class:`~pynwb.core.NWBDataInterface` class.
In most cases, you will not need to interact with the :py:class:`~pynwb.core.NWBDataInterface` class directly.
More commonly, you will be creating instances of classes that extend this class.


.. seealso::

    For your reference, NWB defines the following main analysis :py:class:`~pynwb.core.NWBDataInterface` subtypes:

    * **Behavior:** :py:class:`~pynwb.behavior.BehavioralEpochs`,
      :py:class:`~pynwb.behavior.BehavioralEvents`,
      :py:class:`~pynwb.behavior.BehavioralTimeSeries`,
      :py:class:`~pynwb.behavior.CompassDirection`,
      :py:class:`~pynwb.behavior.PupilTracking`,
      :py:class:`~pynwb.behavior.Position`,
      :py:class:`~pynwb.behavior.EyeTracking`.

    * **Extracellular electrophysiology:** :py:class:`~pynwb.ecephys.EventDetection`,
      :py:class:`~pynwb.ecephys.EventWaveform`,
      :py:class:`~pynwb.ecephys.FeatureExtraction`,
      :py:class:`~pynwb.ecephys.FilteredEphys`,
      :py:class:`~pynwb.ecephys.LFP`.

    * **Optical physiology:** :py:class:`~pynwb.ophys.DfOverF`,
      :py:class:`~pynwb.ophys.Fluorescence`,
      :py:class:`~pynwb.ophys.ImageSegmentation`,
      :py:class:`~pynwb.ophys.MotionCorrection`.

    * **Others:** :py:class:`~pynwb.retinotopy.ImagingRetinotopy`,
      :py:class:`~pynwb.base.Images`.

    * **TimeSeries:** Any :ref:`timeseries_overview` is also a subclass of :py:class:`~pynwb.core.NWBDataInterface`
      and can be used anywhere :py:class:`~pynwb.core.NWBDataInterface` is allowed.

.. note::

    In addition to :py:class:`~pynwb.core.NWBContainer`, which functions as a common base type for Group objects,
    :py:class:`~pynwb.core.NWBData` provides a common base for the specification of datasets in the NWB format.

"""

####################
# .. _basics_nwbfile:
#
# The NWB file
# ------------
#

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_file.png'
from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBFile
import numpy as np

start_time = datetime(2017, 4, 3, 11, tzinfo=tzlocal())
create_date = datetime(2017, 4, 15, 12, tzinfo=tzlocal())

nwbfile = NWBFile(
    session_description='demonstrate NWBFile basics',
    identifier='NWB123',
    session_start_time=start_time
)

####################
# .. _basic_timeseries:
#
# Time series data
# ----------------
#
# PyNWB stores time series data using the :py:class:`~pynwb.base.TimeSeries` class and its subclasses.
# The main components of a :py:class:`~pynwb.base.TimeSeries` are the *data* and the *timestamps*.
# You will also need to supply the name and unit of measurement for *data*.

from pynwb import TimeSeries

data = list(range(100, 200, 10))
timestamps = list(range(10))
test_ts = TimeSeries(name='test_timeseries', data=data, unit='m', timestamps=timestamps)

####################
# Alternatively, if your recordings are sampled at a uniform rate, you can supply *starting_time*
# and *rate*.

rate_ts = TimeSeries(name='test_timeseries', data=data, unit='m', starting_time=0.0, rate=1.0)

####################
# Using this scheme says that this :py:class:`~pynwb.base.TimeSeries` started recording 0 seconds after
# *start_time* stored in the :py:class:`~pynwb.file.NWBFile` and sampled every second.
#
# :py:class:`~pynwb.base.TimeSeries` objects can be added directly to your :py:class:`~pynwb.file.NWBFile` using
# the methods :py:meth:`~pynwb.file.NWBFile.add_acquisition`, :py:meth:`~pynwb.file.NWBFile.add_stimulus`
# and :py:meth:`~pynwb.file.NWBFile.add_stimulus_template`. Which method you use depends on the source of the
# data: use :py:meth:`~pynwb.file.NWBFile.add_acquisition` to indicated *acquisition* data,
# :py:meth:`~pynwb.file.NWBFile.add_stimulus` to indicate *stimulus* data, and
# :py:meth:`~pynwb.file.NWBFile.add_stimulus_template` to store stimulus templates.

nwbfile.add_acquisition(test_ts)

####################
# Access the :py:class:`~pynwb.base.TimeSeries` object `'test_timeseries'` from *acquisition* using

nwbfile.acquisition['test_timeseries']
####################
# or
nwbfile.get_acquisition('test_timeseries')

####################
# .. _basic_writing:
#
# Writing an NWB file
# -------------------
#
# NWB I/O is carried out using the :py:class:`~pynwb.NWBHDF5IO` class [#]_. This class is responsible
# for mapping an :py:class:`~pynwb.file.NWBFile` object into HDF5 according to the NWB schema.
#
# To write an :py:class:`~pynwb.file.NWBFile`, use the :py:meth:`~hdmf.backends.io.HDMFIO.write` method.

from pynwb import NWBHDF5IO

io = NWBHDF5IO('example_file_path.nwb', mode='w')
io.write(nwbfile)
io.close()

####################
# You can also use :py:meth:`~pynwb.NWBHDF5IO` as a context manager:

with NWBHDF5IO('example_file_path.nwb', 'w') as io:
    io.write(nwbfile)

####################
# .. _basic_reading:
#
# Reading an NWB file
# -------------------
#
# As with writing, reading is also carried out using the :py:class:`~pynwb.NWBHDF5IO` class.
# To read the NWB file we just wrote, use another :py:class:`~pynwb.NWBHDF5IO` object,
# and use the :py:meth:`~hdmf.backends.io.HDMFIO.read` method to retrieve an
# :py:class:`~pynwb.file.NWBFile` object.

io = NWBHDF5IO('example_file_path.nwb', 'r')
nwbfile_in = io.read()

####################
# .. _basic_retrieving_data:
#
# Retrieving data from an NWB file
# --------------------------------

test_timeseries_in = nwbfile_in.acquisition['test_timeseries']
print(test_timeseries_in)

####################
# ::
#
#    test_timeseries <class 'pynwb.base.TimeSeries'>
#    Fields:
#      comments: no comments
#      conversion: 1.0
#      data: <HDF5 dataset "data": shape (10,), type "<i8">
#      description: no description
#      interval: 1
#      resolution: 0.0
#      timestamps: <HDF5 dataset "timestamps": shape (10,), type "<f8">
#      timestamps_unit: Seconds
#      unit: SIunit

####################
# Accessing the data field, you will notice that it does not return the data values, but instead an HDF5 dataset.

print(test_timeseries_in.data)

####################
# ::
#
#   <HDF5 dataset "data": shape (10,), type "<i8">
#
# This object lets you only read in a section of the dataset without reading the entire thing.

print(test_timeseries_in.data[:2])

####################
# ::
#
#   [100 110]
#
# To load the entire dataset, use `[:]`.

print(test_timeseries_in.data[:])
io.close()

####################
# ::
#
#   [100 110 120 130 140 150 160 170 180 190]
#
# If you use :py:class:`~pynwb.NWBHDF5IO` as a context manager during read, be aware that the
# :py:class:`~pynwb.NWBHDF5IO` gets closed and when the context completes and the data will not be
# available outside of the context manager [#]_.

####################
# Adding More Data
# ----------------
#
# The following illustrates basic data organizational structures that are used throughout NWB:N.
#
# .. _reuse_timestamps:
#
# Reusing timestamps
# ~~~~~~~~~~~~~~~~~~
#
# When working with multi-modal data, it can be convenient and efficient to store timestamps once and associate multiple
# data with the single timestamps instance. PyNWB enables this by letting you reuse timestamps across
# :class:`~pynwb.base.TimeSeries` objects. To reuse a :class:`~pynwb.base.TimeSeries` timestamps in a new
# :class:`~pynwb.base.TimeSeries`, pass the existing :class:`~pynwb.base.TimeSeries` as the new
# :class:`~pynwb.base.TimeSeries` timestamps:

data = list(range(101, 201, 10))
reuse_ts = TimeSeries('reusing_timeseries', data, 'SIunit', timestamps=test_ts)

####################
# .. _basic_data_interfaces:
#
# Data interfaces
# ---------------
#
# NWB provides the concept of a *data interface*--an object for a standard
# storage location of specific types of data--through the :py:class:`~pynwb.core.NWBDataInterface` class.
# For example, :py:class:`~pynwb.behavior.Position` provides a container that holds one or more
# :py:class:`~pynwb.behavior.SpatialSeries` objects. :py:class:`~pynwb.behavior.SpatialSeries` is a subtype of
# :py:class:`~pynwb.base.TimeSeries` that represents the spatial position of an animal over time. By putting
# your position data into a :py:class:`~pynwb.behavior.Position` container, downstream users and
# tools know where to look to retrieve position data. For a comprehensive list of available data interfaces, see the
# :ref:`overview page <modules_overview>`. Here is how to create a :py:class:`~pynwb.behavior.Position` object
# named '`Position'` [#]_.

from pynwb.behavior import Position

position = Position()

####################
# You can add objects to a data interface as a method of the data interface:

position.create_spatial_series(name='position1',
                               data=np.linspace(0, 1, 20),
                               rate=50.,
                               reference_frame='starting gate')

####################
# or you can add pre-existing objects:

from pynwb.behavior import SpatialSeries

spatial_series = SpatialSeries(name='position2',
                               data=np.linspace(0, 1, 20),
                               rate=50.,
                               reference_frame='starting gate')

position.add_spatial_series(spatial_series)

####################
# or include the object during construction:

spatial_series = SpatialSeries(name='position2',
                               data=np.linspace(0, 1, 20),
                               rate=50.,
                               reference_frame='starting gate')

position = Position(spatial_series=spatial_series)

####################
# Each data interface stores its own type of data. We suggest you read the documentation for the
# data interface of interest in the :ref:`API documentation <api_docs>` to figure out what data the
# data interface allows and/or requires and what methods you will need to call to add this data.

####################
# .. _basic_procmod:
#
# Processing modules
# ------------------
#
# *Processing modules* are used for storing a set of data interfaces that are related to a particular
# processing workflow. For example, if you want to store the intermediate results of a spike sorting workflow,
# you could create a :py:class:`~pynwb.base.ProcessingModule` that contains data interfaces that represent
# the common first steps in spike sorting e.g. :py:class:`~pynwb.ecephys.EventDetection`,
# :py:class:`~pynwb.ecephys.EventWaveform`,  :py:class:`~pynwb.ecephys.FeatureExtraction`. The final results of
# the sorting could then be stored in the top-level :py:class:`~pynwb.misc.Units` table (see below).
# Derived preprocessed data should go in a processing module, which you can create using
# :py:meth:`~pynwb.file.NWBFile.create_processing_module`:

behavior_module = nwbfile.create_processing_module(name='behavior',
                                                   description='preprocessed behavioral data')

####################
# or by directly calling the constructor and adding to the :py:class:`~pynwb.file.NWBFile` using
# :py:meth:`~pynwb.file.NWBFile.add_processing_module`:

from pynwb import ProcessingModule

ecephys_module = ProcessingModule(name='ecephys',
                                  description='preprocessed extracellular electrophysiology')
nwbfile.add_processing_module(ecephys_module)

####################
# Best practice is to use the NWB schema module names as processing module names where appropriate.
# These are: 'behavior', 'ecephys', 'icephys', 'ophys', 'ogen', 'retinotopy', and 'misc'. You may also create
# a processing module with a custom name. Once these processing modules are added, access them with

nwbfile.processing

####################
# which returns a `dict`:
# ::
#
#    {'behavior':
#     behavior <class 'pynwb.base.ProcessingModule'>
#     Fields:
#       data_interfaces: { Position <class 'pynwb.behavior.Position'> }
#       description: preprocessed behavioral data, 'ecephys':
#     ecephys <class 'pynwb.base.ProcessingModule'>
#     Fields:
#       data_interfaces: { }
#       description: preprocessed extracellular electrophysiology}
#
# :py:class:`~pynwb.core.NWBDataInterface` objects can be added to the behavior :ref:`ProcessingModule <basic_procmod>`.

nwbfile.processing['behavior'].add(position)

####################
# Time Intervals
# --------------
#
# .. _basic_trials:
#
# Trials
# ^^^^^^
#
# Trials can be added to an NWB file using the methods :py:meth:`~pynwb.file.NWBFile.add_trial`
# and :py:meth:`~pynwb.file.NWBFile.add_trial_column`. Together, these methods maintains a
# table-like structure that can define arbitrary columns without having to go through the
# extension process.
#
# By default, NWBFile only requires trial start time and trial end time. Additional columns
# can be added using :py:meth:`~pynwb.file.NWBFile.add_trial_column`. This method takes a name
# for the column and a description of what the column stores. You do not need to supply data
# type, as this will inferred.
# Once all columns have been added, trial data can be populated using :py:meth:`~pynwb.file.NWBFile.add_trial`.
#
# Lets add an additional column and some trial data.

nwbfile.add_trial_column(name='stim', description='the visual stimuli during the trial')

nwbfile.add_trial(start_time=0.0, stop_time=2.0, stim='person')
nwbfile.add_trial(start_time=3.0, stop_time=5.0, stim='ocean')
nwbfile.add_trial(start_time=6.0, stop_time=8.0, stim='desert')

####################
# Tabular data such as trials can be converted to a `pandas.DataFrame`.

print(nwbfile.trials.to_dataframe())

####################
# ::
#
#           start_time  stop_time    stim
#       id
#       0          0.0        2.0  person
#       1          3.0        5.0   ocean
#       2          6.0        8.0  desert
#
# .. _basic_epochs:
#
# Epochs
# ^^^^^^
#
# Epochs can be added to an NWB file using the method :py:meth:`~pynwb.file.NWBFile.add_epoch`.
# The first and second arguments are the start time and stop times, respectively.
# The third argument is one or more tags for labeling the epoch, and the fourth argument is a
# list of all the :py:class:`~pynwb.base.TimeSeries` that the epoch applies
# to.

nwbfile.add_epoch(2.0, 4.0, ['first', 'example'], [test_ts, ])
nwbfile.add_epoch(6.0, 8.0, ['second', 'example'], [test_ts, ])

####################
# Other time intervals
# ^^^^^^^^^^^^^^^^^^^^
# Both ``epochs`` and ``trials`` are of of data type :py:class:`~pynwb.epoch.TimeIntervals`, which is a type of
# ``DynamicTable`` for storing information about time intervals. ``"epochs"`` and ``"trials"``
# are the two default names for :py:class:`~pynwb.base.TimeIntervals` objects, but you can also add your own

from pynwb.epoch import TimeIntervals

sleep_stages = TimeIntervals(
    name="sleep_stages",
    description="intervals for each sleep stage as determined by EEG",
)

sleep_stages.add_column(name="stage", description="stage of sleep")
sleep_stages.add_column(name="confidence", description="confidence in stage (0-1)")

sleep_stages.add_row(start_time=0.3, stop_time=0.5, stage=1, confidence=.5)
sleep_stages.add_row(start_time=0.7, stop_time=0.9, stage=2, confidence=.99)
sleep_stages.add_row(start_time=1.3, stop_time=3.0, stage=3, confidence=0.7)

nwbfile.add_time_intervals(sleep_stages)

####################
# .. _basic_units:
#
# Units
# ------
#
# Units are putative cells in your analysis. Unit metadata can be added to an NWB file using the methods
# :py:meth:`~pynwb.file.NWBFile.add_unit` and :py:meth:`~pynwb.file.NWBFile.add_unit_column`. These methods
# work like the methods for adding trials described :ref:`above <basic_trials>`
#
# A unit is only required to contain a unique integer identifier in the 'id' column
# (this will be automatically assigned if not provided). Additional optional values for each unit
# include: `spike_times`, `electrodes`, `electrode_group`, `obs_intervals`, `waveform_mean`, and `waveform_sd`.
# Additional user-defined columns can be added using :py:meth:`~pynwb.file.NWBFile.add_unit_column`. Like
# :py:meth:`~pynwb.file.NWBFile.add_trial_column`, this method also takes a name
# for the column, a description of what the column stores and does not need a data type.
# Once all columns have been added, unit data can be populated using :py:meth:`~pynwb.file.NWBFile.add_unit`.
#
# When providing `spike_times`, you may also wish to specify the time intervals during which the unit was
# being observed, so that it is possible to distinguish times when the unit was silent from times when the
# unit was not being recorded (and thus correctly compute firing rates, for example). This information
# should be provided as a list of [start, end] time pairs in the `obs_intervals` field. If `obs_intervals` is
# provided, then all entries in `spike_times` should occur within one of the listed intervals. In the example
# below, all 3 units are observed during the time period from 1 to 10 s and fired spikes during that period.
# Units 2 and 3 were also observed during the time period from 20-30s; but only unit 2 fired spikes in that
# period.
#
# Lets specify some unit metadata and then add some units:

nwbfile.add_unit_column('location', 'the anatomical location of this unit')
nwbfile.add_unit_column('quality', 'the quality for the inference of this unit')

nwbfile.add_unit(id=1, spike_times=[2.2, 3.0, 4.5],
                 obs_intervals=[[1, 10]], location='CA1', quality=0.95)
nwbfile.add_unit(id=2, spike_times=[2.2, 3.0, 25.0, 26.0],
                 obs_intervals=[[1, 10], [20, 30]], location='CA3', quality=0.85)
nwbfile.add_unit(id=3, spike_times=[1.2, 2.3, 3.3, 4.5],
                 obs_intervals=[[1, 10], [20, 30]], location='CA1', quality=0.90)

####################
# Now we overwrite the file with all of the data

with NWBHDF5IO('example_file_path.nwb', 'w') as io:
    io.write(nwbfile)

####################
# .. _units_fields_ref:
#
# .. note::
#    The Units table has some predefined optional columns. Please review the documentation for
#    :py:meth:`~pynwb.file.NWBFile.add_unit` before adding custom columns.

####################
# .. _basic_appending:
#
# Appending to an NWB file
# ------------------------
#
# Using functionality discussed above, NWB allows appending to files. To append to a file, you must read the file, add
# new components, and then write the file. Reading and writing is carried out using :py:class:`~pynwb.NWBHDF5IO`.
# When reading the NWBFile, you must specify that you intend to modify it by setting the *mode* argument in the
# :py:class:`~pynwb.NWBHDF5IO` constructor to ``'a'``. After you have read the file, you can add [#]_ new data to it
# using the standard write/add functionality demonstrated above.
#
# Let's see how this works by adding another :py:class:`~pynwb.base.TimeSeries` to the BehavioralTimeSeries interface
# we created above.
#
# First, read the file and get the interface object.

io = NWBHDF5IO('example_file_path.nwb', mode='a')
nwbfile = io.read()
position = nwbfile.processing['behavior'].data_interfaces['Position']

####################
# Next, add a new :py:class:`~pynwb.behavior.SpatialSeries`.

data = list(range(300, 400, 10))
timestamps = list(range(10))
test_spatial_series = SpatialSeries('test_spatialseries2', data,
                                    reference_frame='starting_gate',
                                    timestamps=timestamps)
position.add_spatial_series(test_spatial_series)

####################
# Finally, write the changes back to the file and close it.

io.write(nwbfile)
io.close()

####################
# .. [#] HDF5 is currently the only backend supported by NWB.
#
# .. [#] Neurodata sets can be *very* large, so individual components of the dataset are only loaded into memory when
#    you request them. This functionality is only possible if an open file handle is kept around until users want to
#    load data.
#
# .. [#] Some data interface objects have a default name. This default name is the type of the data interface. For
#    example, the default name for :py:class:`~pynwb.ophys.ImageSegmentation` is "ImageSegmentation" and the default
#    name for :py:class:`~pynwb.ecephys.EventWaveform` is "EventWaveform".
#
# .. [#] NWB only supports *adding* to files. Removal and modifying of existing data is not allowed.

####################
# .. _hck04: https://github.com/NeurodataWithoutBorders/nwb_hackathons/tree/master/HCK04_2018_Seattle
