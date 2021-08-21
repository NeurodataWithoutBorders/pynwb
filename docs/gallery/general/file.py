"""
.. _basics:

NWB basics
==========

This example will focus on the basics of working with an :py:class:`~pynwb.file.NWBFile` object,
including I/O operations and introduction to the basic data types.

.. contents:: :local:
    :depth: 3

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
"""

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_file.png'
import numpy as np
from pynwb import NWBFile, TimeSeries
from pynwb.file import Subject
from pynwb.behavior import SpatialSeries, Position
from datetime import datetime
from dateutil import tz

####################
# The NWB file
# ------------------------------
#
# An :py:class:`~pynwb.file.NWBFile` represents a single session of an experiment.
# Each :py:class:`~pynwb.file.NWBFile` must have a session description, identifier, and session start time.
# Importantly, the session start time is the reference time for all timestamps in the file.
# For instance, an event with a timestamp of 0 in the file means the event
# occurred exactly at the session start time.
#
# Create an :py:class:`~pynwb.file.NWBFile` object with the required fields
# (``session_description``, ``identifier``, ``session_start_time``) and additional metadata.
#
# We recommend using keyword arguments for clarity when constructing :py:class:`~pynwb` objects.


session_start_time = datetime(2018, 4, 25, 2, 30, 3,
                              tzinfo=tz.gettz('US/Pacific'))

nwbfile = NWBFile(
    session_description='Mouse exploring an open field',     # required
    identifier='Mouse5_Day3',                                # required
    session_start_time=session_start_time,                   # required
    session_id='session_1234',                               # optional
    experimenter='My Name',                                  # optional
    lab='My Lab Name',                                       # optional
    institution='University of My Institution',              # optional
    related_publications='DOI:10.1016/j.neuron.2016.12.011'  # optional
)
print(nwbfile)

####################
# .. _basic_subject:
# Subject information
# ------------------------------
#
# In the :py:class:`~pynwb.file.Subject` object we can store information about the experimental subject,
# such as age, species, genotype, sex, and a description.
#
# image placeholder
#
# :py:class:`~pynwb.file.Subject` fields are all free-form text (any format will be valid),
# however it is recommended to follow particular conventions to help software tools interpret the data:
#
# * **age**: `ISO 8601 Duration format <https://en.wikipedia.org/wiki/ISO_8601#Durations>`_, e.g., ``"P90D"`` for 90 days old
# * **species**: The formal latin binomial nomenclature, e.g., ``"Mus musculus"``, ``"Homo sapiens"``
# * **sex**: Single letter abbreviation, e.g., ``"F"`` (female), ``"M"`` (male), ``"U"`` (unknown), and ``"O"`` (other)
#
# Add the subject information to the :py:class:`~pynwb.file.NWBFile`
# by setting the ``subject`` field to the new :py:class:`~pynwb.file.Subject` object.

nwbfile.subject = Subject(
    subject_id='001',
    age='P90D',
    description='mouse 5',
    species='Mus musculus',
    sex='M'
)

####################
# .. _basic_data_interfaces:
#
# Basic Data Interfaces
# ------------------------------
#
# **Data Interfaces** are objects for storing specific types of data in a standardized way --
# through the :py:class:`~pynwb.core.NWBDataInterface` class.
# This tutorial covers the basic data interfaces (e.g. :py:class:`~pynwb.base.TimeSeries`,
# :py:class:`~pynwb.behavior.Position`). For a comprehensive list of available data interfaces,
# see the :ref:`overview page <modules_overview>`.

####################
# .. _basic_timeseries:
#
# Time Series data
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# :py:class:`~pynwb.base.TimeSeries` is a common base class for measurements sampled over time,
# and provides fields for ``data`` and ``timestamps`` (regularly or irregularly sampled).
# You will also need to supply the ``name`` and ``unit`` of measurement
# (`SI unit <https://en.wikipedia.org/wiki/International_System_of_Units>`_) for ``data``.
# For instance, we can store a :py:class:`~pynwb.base.TimeSeries` data where recording started
# ``0.0`` seconds after ``start_time`` and sampled every second:

data = list(range(100, 200, 10))
time_series_with_rate = TimeSeries(name='test_timeseries',
                                   data=data,
                                   unit='m',
                                   starting_time=0.0,
                                   rate=1.0)

####################
# For irregularly sampled recordings, we need to provide the ``timestamps`` for the ``data``:

timestamps = list(range(10))
time_series_with_timestamps = TimeSeries(name='test_timeseries',
                                         data=data,
                                         unit='m',
                                         timestamps=timestamps)

####################
# :py:class:`~pynwb.base.TimeSeries` objects can be added directly to :py:class:`~pynwb.file.NWBFile` using
# the :py:meth:`~pynwb.file.NWBFile.add_acquisition`, :py:meth:`~pynwb.file.NWBFile.add_stimulus`
# or :py:meth:`~pynwb.file.NWBFile.add_stimulus_template` methods depending on the source of data.
# Use :py:meth:`~pynwb.file.NWBFile.add_acquisition` to  add *acquisition* data (raw, acquired data that should never change);
# :py:meth:`~pynwb.file.NWBFile.add_stimulus` to add *stimulus* data; and use
# :py:meth:`~pynwb.file.NWBFile.add_stimulus_template` to store stimulus templates.
# Here, we will add it as *acquisition* data:

nwbfile.add_acquisition(time_series_with_timestamps)

####################
# We can access the :py:class:`~pynwb.base.TimeSeries` object ``'test_timeseries'``
# in :py:class:`~pynwb.file.NWBFile` from ``acquisition``:

nwbfile.acquisition['test_timeseries']

####################
# or using the :py:meth:`~pynwb.file.NWBFile.get_acquisition` method:
nwbfile.get_acquisition('test_timeseries')


####################
# .. _basic_spatialseries:
#
# Spatial Series and Position
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# :py:class:`~pynwb.behavior.SpatialSeries` is a subclass of :py:class:`~pynwb.base.TimeSeries`
# that represents the spatial position of an animal over time.
# Create a :py:class:`~pynwb.behavior.SpatialSeries` object named 'SpatialSeries' with some fake data.

# create fake data with shape (50, 2)
# the first dimension should always represent time
position_data = np.array([np.linspace(0, 10, 50),
                          np.linspace(0, 8, 50)]).T
position_timestamps = np.linspace(0, 50) / 200

spatial_series_obj = SpatialSeries(
    name='SpatialSeries',
    description='(x,y) position in open field',
    data=position_data,
    timestamps=position_timestamps,
    reference_frame='(0,0) is bottom left corner'
)
print(spatial_series_obj)

####################
# To help data analysis and visualization tools know that this :py:class:`~pynwb.behavior.SpatialSeries` object
# represents the position of the subject, store the :py:class:`~pynwb.behavior.SpatialSeries` object inside
# of a :py:class:`~pynwb.behavior.Position` object, which can hold one or more :py:class:`~pynwb.behavior.SpatialSeries` objects.
# Create a :py:class:`~pynwb.behavior.Position` object named ``"Position"`` [#]_.

# name is set to "Position" by default
position_obj = Position(spatial_series=spatial_series_obj)

####################
# .. _basic_procmod:
#
# Processing Modules
# ------------------
#
# :py:class:`~pynwb.base.ProcessingModule` is a container for data interfaces that are related to a particular
# processing workflow. NWB differentiates between raw, acquired data (*acquisition*), which should never change,
# and processed data (*processing*), which are the results of preprocessing algorithms and could change.
# Processing modules can be thought of as folders within the file for storing the related processed data.
#
# Read the :ref:`API documentation <api_docs>` for the data interface of interest to figure out what data the data
# interface allows and/or requires and what methods you will need to call to add this data.
#
# .. note:: Best practice is to use the NWB schema module names as processing module names where appropriate.
#    These are: ``"behavior"``, ``"ecephys"``, ``"icephys"``, ``"ophys"``, ``"ogen"``, ``"retinotopy"``, and ``"misc"``.
#
# Behavior Processing Module
# ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
#
# Let's assume that the subject's position was computed from a video tracking algorithm,
# so it would be classified as processed data.
#
# Create a processing module called ``"behavior"`` for storing behavioral data in the :py:class:`~pynwb.file.NWBFile`
# and add the :py:class:`~pynwb.behavior.Position` object to the processing module using the
# :py:meth:`~pynwb.file.NWBFile.create_processing_module` method:


behavior_module = nwbfile.create_processing_module(
    name='behavior',
    description='processed behavioral data'
)
behavior_module.add(position_obj)

####################
# Once the behavior processing module is added to the :py:class:`~pynwb.file.NWBFile,
# you can access it with:

print(nwbfile.processing['behavior'])

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
# Time Intervals
# --------------
#
# .. _basic_trials:
#
# Trials
# ~~~~~~~~~~~~~~~~~~~~~~
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

nwbfile.add_trial_column(name='stim',
                         description='the visual stimuli during the trial')

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
# ~~~~~~~~~~~~~~~~~~~~~~
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
# ~~~~~~~~~~~~~~~~~~~~~~
# Both ``epochs`` and ``trials`` are of of data type :py:class:`~pynwb.epoch.TimeIntervals`, which is a type of
# ``DynamicTable`` for storing information about time intervals. ``"epochs"`` and ``"trials"``
# are the two default names for :py:class:`~pynwb.base.TimeIntervals` objects, but you can also add your own

from pynwb.epoch import TimeIntervals

sleep_stages = TimeIntervals(
    name="sleep_stages",
    description="intervals for each sleep stage as determined by EEG",
)

sleep_stages.add_column(name="stage", description="stage of sleep")
sleep_stages.add_column(name="confidence",
                        description="confidence in stage (0-1)")

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
nwbfile.add_unit_column('quality',
                        'the quality for the inference of this unit')

nwbfile.add_unit(id=1, spike_times=[2.2, 3.0, 4.5],
                 obs_intervals=[[1, 10]], location='CA1', quality=0.95)
nwbfile.add_unit(id=2, spike_times=[2.2, 3.0, 25.0, 26.0],
                 obs_intervals=[[1, 10], [20, 30]], location='CA3',
                 quality=0.85)
nwbfile.add_unit(id=3, spike_times=[1.2, 2.3, 3.3, 4.5],
                 obs_intervals=[[1, 10], [20, 30]], location='CA1',
                 quality=0.90)

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
# .. [#] Some data interface objects have a default name. This default name is the type of the data interface. For
#    example, the default name for :py:class:`~pynwb.ophys.ImageSegmentation` is "ImageSegmentation" and the default
#    name for :py:class:`~pynwb.ecephys.EventWaveform` is "EventWaveform".
#
# .. [#] HDF5 is currently the only backend supported by NWB.
#
# .. [#] Neurodata sets can be *very* large, so individual components of the dataset are only loaded into memory when
#    you request them. This functionality is only possible if an open file handle is kept around until users want to
#    load data.
#
# .. [#] NWB only supports *adding* to files. Removal and modifying of existing data is not allowed.

####################
# .. _hck04: https://github.com/NeurodataWithoutBorders/nwb_hackathons/tree/master/HCK04_2018_Seattle
