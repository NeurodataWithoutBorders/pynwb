"""
.. _basics:

NWB File Basics
===============

This example will focus on the basics of working with an :py:class:`~pynwb.file.NWBFile` object,
including writing and reading of an NWB file, and giving you an introduction to the basic data types.
Before we dive into code showing how to use an :py:class:`~pynwb.file.NWBFile`, we first provide
a brief overview of the basic concepts of NWB.

.. _basics_background:

Background: Basic concepts
--------------------------

In the `NWB Format <https://nwb-schema.readthedocs.io>`_, each experiment session is typically
represented by a separate NWB file. NWB files are represented in PyNWB by :py:class:`~pynwb.file.NWBFile`
objects which provide functionality for creating and retrieving:

 * :ref:`timeseries_overview` datasets -- objects for storing time series data
 * :ref:`modules_overview` -- objects for storing and grouping analyses, and
 * experiment metadata and other metadata related to data provenance.

The following sections describe the :py:class:`~pynwb.base.TimeSeries` and :py:class:`~pynwb.base.ProcessingModule`
classes in further detail.

.. _timeseries_overview:

TimeSeries
^^^^^^^^^^

:py:class:`~pynwb.base.TimeSeries` objects store time series data and correspond to the *TimeSeries* specifications
provided by the `NWB Format`_. Like the NWB specification, :py:class:`~pynwb.base.TimeSeries` Python objects
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
      :py:class:`~pynwb.image.OpticalSeries`,
      :py:class:`~pynwb.ophys.OnePhotonSeries`, and
      :py:class:`~pynwb.ophys.TwoPhotonSeries` types.
      Other related time series types are:
      :py:class:`~pynwb.image.IndexSeries`,
      :py:class:`~pynwb.ophys.RoiResponseSeries`.

    * **Others:** :py:class:`~pynwb.ogen.OptogeneticSeries`,
      :py:class:`~pynwb.behavior.SpatialSeries`,
      :py:class:`~pynwb.misc.DecompositionSeries`,
      :py:class:`~pynwb.misc.AnnotationSeries`,
      :py:class:`~pynwb.misc.AbstractFeatureSeries`,
      :py:class:`~pynwb.misc.IntervalSeries`.


.. _modules_overview:

Processing Modules
^^^^^^^^^^^^^^^^^^

Processing modules are objects that group together common analyses done during processing of data. They
often hold data of different processing/analysis data types.

.. seealso::

    For your reference, NWB defines the following main processing/analysis data types:

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

    * **Others:** :py:class:`~pynwb.base.Images`.

    * **TimeSeries:** Any :py:class:`~pynwb.base.TimeSeries` can be used to store processing/analysis data.

NWB organizes data into different groups depending on the type of data. Groups can be thought of
as folders within the file. Here are some of the groups within an :py:class:`~pynwb.file.NWBFile` and the types of
data they are intended to store:

* **acquisition**: raw, acquired data that should never change
* **processing**: processed data, typically the results of preprocessing algorithms and could change
* **analysis**: results of data analysis
* **stimuli**: stimuli used in the experiment (e.g., images, videos, light pulses)

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:

"""

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_file.png'

from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil import tz

from pynwb import NWBHDF5IO, NWBFile, TimeSeries
from pynwb.behavior import Position, SpatialSeries
from pynwb.file import Subject

####################
# .. _basics_nwbfile:
#
# The NWB file
# ------------
#
# An :py:class:`~pynwb.file.NWBFile` represents a single session of an experiment.
# Each :py:class:`~pynwb.file.NWBFile` must have a session description, identifier, and session start time.
# Importantly, the session start time is the reference time for all timestamps in the file.
# For instance, an event with a timestamp of 0 in the file means the event
# occurred exactly at the session start time.
#
# Create an :py:class:`~pynwb.file.NWBFile` object with the required fields
# (:py:attr:`~pynwb.file.NWBFile.session_description`, :py:attr:`~pynwb.file.NWBFile.identifier`,
# :py:attr:`~pynwb.file.NWBFile.session_start_time`) and additional metadata.
#
# .. note::
#     Use keyword arguments when constructing :py:class:`~pynwb.file.NWBFile` objects.
#

session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))

nwbfile = NWBFile(
    session_description="Mouse exploring an open field",  # required
    identifier=str(uuid4()),  # required
    session_start_time=session_start_time,  # required
    session_id="session_1234",  # optional
    experimenter=[
        "Baggins, Bilbo",
    ],  # optional
    lab="Bag End Laboratory",  # optional
    institution="University of Middle Earth at the Shire",  # optional
    experiment_description="I went on an adventure to reclaim vast treasures.",  # optional
    keywords=["behavior", "exploration", "wanderlust"],  # optional
    related_publications="doi:10.1016/j.neuron.2016.12.011",  # optional
)
nwbfile

####################
# .. note::
#
#     See the `NWBFile Best Practices <https://nwbinspector.readthedocs.io/en/dev/best_practices/nwbfile_metadata.html#file-metadata>`_
#     for detailed information about the arguments to
#     :py:class:`~pynwb.file.NWBFile`

####################
# .. _basic_subject:
#
# Subject Information
# -------------------
#
# In the :py:class:`~pynwb.file.Subject` object we can store information about the experiment subject,
# such as ``age``, ``species``, ``genotype``, ``sex``, and a ``description``.
#
# .. only:: html
#
#   .. image:: ../../_static/Subject.svg
#     :width: 150
#     :alt: subject UML diagram
#     :align: center
#
# .. only:: latex
#
#   .. image:: ../../_static/Subject.png
#     :width: 150
#     :alt: subject UML diagram
#     :align: center
#
# The fields in the :py:class:`~pynwb.file.Subject` object are all free-form text (any format will be valid),
# however it is recommended to follow particular conventions to help software tools interpret the data:
#
# * **age**: `ISO 8601 Duration format <https://en.wikipedia.org/wiki/ISO_8601#Durations>`_, e.g., ``"P90D"`` for 90
#   days old
# * **species**: The formal Latin binomial nomenclature, e.g., ``"Mus musculus"``, ``"Homo sapiens"``
# * **sex**: Single letter abbreviation, e.g., ``"F"`` (female), ``"M"`` (male), ``"U"`` (unknown), and ``"O"`` (other)
#
# Add the subject information to the :py:class:`~pynwb.file.NWBFile`
# by setting the ``subject`` field to a new :py:class:`~pynwb.file.Subject` object.

subject = Subject(
    subject_id="001",
    age="P90D",
    description="mouse 5",
    species="Mus musculus",
    sex="M",
)

nwbfile.subject = subject
subject

####################
# .. _basic_timeseries:
#
# Time Series Data
# ----------------
#
# :py:class:`~pynwb.base.TimeSeries` is a common base class for measurements sampled over time,
# and provides fields for ``data`` and ``timestamps`` (regularly or irregularly sampled).
# You will also need to supply the ``name`` and ``unit`` of measurement
# (`SI unit <https://en.wikipedia.org/wiki/International_System_of_Units>`_).
#
# .. image:: ../../_static/TimeSeries.png
#   :width: 200
#   :alt: timeseries UML diagram
#   :align: center
#
# For instance, we can store a :py:class:`~pynwb.base.TimeSeries` data where recording started
# ``0.0`` seconds after ``start_time`` and sampled every second (1 Hz):

data = np.arange(100, 200, 10)
time_series_with_rate = TimeSeries(
    name="test_timeseries",
    description="an example time series",
    data=data,
    unit="m",
    starting_time=0.0,
    rate=1.0,
)
time_series_with_rate

####################
# For irregularly sampled recordings, we need to provide the ``timestamps`` for the ``data``:

timestamps = np.arange(10.)
time_series_with_timestamps = TimeSeries(
    name="test_timeseries",
    description="an example time series",
    data=data,
    unit="m",
    timestamps=timestamps,
)
time_series_with_timestamps

####################
# :py:class:`~pynwb.base.TimeSeries` objects can be added directly to :py:class:`~pynwb.file.NWBFile` using:
#
# * :py:meth:`.NWBFile.add_acquisition` to add *acquisition* data (raw, acquired data that should never change),
# * :py:meth:`.NWBFile.add_stimulus` to add *stimulus* data, or
# * :py:meth:`.NWBFile.add_stimulus_template` to store *stimulus templates*.
#

nwbfile.add_acquisition(time_series_with_timestamps)

####################
# We can access the :py:class:`~pynwb.base.TimeSeries` object ``'test_timeseries'``
# in :py:class:`~pynwb.file.NWBFile` from ``acquisition``:

nwbfile.acquisition["test_timeseries"]

####################
# or using the method :py:meth:`.NWBFile.get_acquisition`:
nwbfile.get_acquisition("test_timeseries")


####################
# .. _basic_spatialseries:
#
# Spatial Series and Position
# ---------------------------
#
# :py:class:`~pynwb.behavior.SpatialSeries` is a subclass of :py:class:`~pynwb.base.TimeSeries`
# that represents the spatial position of an animal over time.
#
# .. only:: html
#
#   .. image:: ../../_static/SpatialSeries.svg
#     :width: 200
#     :alt: spatialseries UML diagram
#     :align: center
#
# .. only:: latex
#
#   .. image:: ../../_static/SpatialSeries.png
#     :width: 200
#     :alt: spatialseries UML diagram
#     :align: center
#
# Create a :py:class:`~pynwb.behavior.SpatialSeries` object named ``"SpatialSeries"`` with some fake data.

# create fake data with shape (50, 2)
# the first dimension should always represent time
position_data = np.array([np.linspace(0, 10, 50), np.linspace(0, 8, 50)]).T
position_timestamps = np.linspace(0, 50).astype(float) / 200

spatial_series_obj = SpatialSeries(
    name="SpatialSeries",
    description="(x,y) position in open field",
    data=position_data,
    timestamps=position_timestamps,
    reference_frame="(0,0) is bottom left corner",
)
spatial_series_obj

####################
# To help data analysis and visualization tools know that this :py:class:`~pynwb.behavior.SpatialSeries` object
# represents the position of the subject, store the :py:class:`~pynwb.behavior.SpatialSeries` object inside
# of a :py:class:`~pynwb.behavior.Position` object, which can hold one or more :py:class:`~pynwb.behavior.SpatialSeries`
# objects.
#
# .. only:: html
#
#   .. image:: ../../_static/Position.svg
#     :width: 450
#     :alt: position UML diagram
#     :align: center
#
# .. only:: latex
#
#   .. image:: ../../_static/Position.png
#     :width: 450
#     :alt: position UML diagram
#     :align: center
#
# Create a :py:class:`~pynwb.behavior.Position` object named ``"Position"`` [#]_.

# name is set to "Position" by default
position_obj = Position(spatial_series=spatial_series_obj)
position_obj

####################
# Behavior Processing Module
# --------------------------
#
# :py:class:`~pynwb.base.ProcessingModule` is a container for data interfaces that are related to a particular
# processing workflow. NWB differentiates between raw, acquired data (*acquisition*), which should never change,
# and processed data (*processing*), which are the results of preprocessing algorithms and could change.
# Processing modules can be thought of as folders within the file for storing the related processed data.
#
# .. tip:: Use the NWB schema module names as processing module names where appropriate.
#    These are: ``"behavior"``, ``"ecephys"``, ``"icephys"``, ``"ophys"``, ``"ogen"``, and ``"misc"``.
#
# Let's assume that the subject's position was computed from a video tracking algorithm,
# so it would be classified as processed data.
#
# Create a processing module called ``"behavior"`` for storing behavioral data in the :py:class:`~pynwb.file.NWBFile`
# and add the :py:class:`~pynwb.behavior.Position` object to the processing module using the method
# :py:meth:`.NWBFile.create_processing_module`:


behavior_module = nwbfile.create_processing_module(
    name="behavior", description="processed behavioral data"
)
behavior_module.add(position_obj)
behavior_module

####################
#
# .. only:: html
#
#   .. image:: ../../_static/Behavior.svg
#     :width: 600
#     :alt: behavior UML diagram
#     :align: center
#
# .. only:: latex
#
#   .. image:: ../../_static/Behavior.png
#     :width: 600
#     :alt: behavior UML diagram
#     :align: center
#
# Once the behavior processing module is added to the :py:class:`~pynwb.file.NWBFile`,
# you can access it with:

nwbfile.processing["behavior"]

####################
# Time Intervals
# --------------
#
# .. _basic_trials:
#
# The following provides a brief introduction to managing annotations in time via
# :py:class:`~pynwb.epoch.TimeIntervals`. See the :ref:`time_intervals` tutorial
# for a more detailed introduction to :py:class:`~pynwb.epoch.TimeIntervals`.
#
# Trials
# ^^^^^^
#
# Trials are stored in :py:class:`~pynwb.epoch.TimeIntervals`, which is
# a subclass of :py:class:`~hdmf.common.table.DynamicTable`.
# :py:class:`~hdmf.common.table.DynamicTable` is used to store
# tabular metadata throughout NWB, including trials, electrodes and sorted units. This
# class offers flexibility for tabular data by allowing required columns, optional
# columns, and custom columns which are not defined in the standard.
#
# .. only:: html
#
#   .. image:: ../../_static/Trials.svg
#     :width: 300
#     :alt: trials UML diagram
#     :align: center
#
# .. only:: latex
#
#   .. image:: ../../_static/Trials.png
#     :width: 300
#     :alt: trials UML diagram
#     :align: center
#
# The ``trials`` :py:class:`~pynwb.epoch.TimeIntervals` class can be thought of
# as a table with this structure:
#
# .. image:: ../../_static/trials_example.png
#   :width: 400
#   :alt: trials table example
#   :align: center
#
# By default, :py:class:`~pynwb.epoch.TimeIntervals` objects only require ``start_time``
# and ``stop_time`` of each trial. Additional columns can be added using
# the method :py:meth:`.NWBFile.add_trial_column`. When all the desired custom columns
# have been defined, use the :py:meth:`.NWBFile.add_trial` method to add each row.
# In this case, we will add one custom column to the trials table named "correct"
# which will take a boolean array, then add two trials as rows of the table.

nwbfile.add_trial_column(
    name="correct",
    description="whether the trial was correct",
)
nwbfile.add_trial(start_time=1.0, stop_time=5.0, correct=True)
nwbfile.add_trial(start_time=6.0, stop_time=10.0, correct=False)

####################
# :py:class:`~hdmf.common.table.DynamicTable` and its subclasses can be converted to a pandas
# :py:class:`~pandas.DataFrame` for convenient analysis using :py:meth:`~hdmf.common.table.DynamicTable.to_dataframe`.

nwbfile.trials.to_dataframe()

####################
# .. _basic_writing:
#
# Writing an NWB file
# -------------------
#
# Writing of an NWB file is carried out using the :py:class:`~pynwb.NWBHDF5IO` class [#]_.
#
# To write an :py:class:`~pynwb.file.NWBFile`, use the :py:meth:`~hdmf.backends.io.HDMFIO.write` method.

io = NWBHDF5IO("basics_tutorial.nwb", mode="w")
io.write(nwbfile)
io.close()

####################
# You can also use :py:meth:`~pynwb.NWBHDF5IO` as a context manager:

with NWBHDF5IO("basics_tutorial.nwb", "w") as io:
    io.write(nwbfile)

####################
# .. _basic_reading:
#
# Reading an NWB file
# -------------------
#
# As with writing, reading is also carried out using the :py:class:`~pynwb.NWBHDF5IO` class.
# To read the NWB file we just wrote, create another :py:class:`~pynwb.NWBHDF5IO` object with the mode set to ``"r"``,
# and use the :py:meth:`~pynwb.NWBHDF5IO.read` method to retrieve an
# :py:class:`~pynwb.file.NWBFile` object.
#
# Data arrays are read passively from the file.
# Accessing the ``data`` attribute of the :py:class:`~pynwb.base.TimeSeries` object
# does not read the data values, but presents an HDF5 object that can be indexed to read data.
# You can use the ``[:]`` operator to read the entire data array into memory.

with NWBHDF5IO("basics_tutorial.nwb", "r") as io:
    read_nwbfile = io.read()
    print(read_nwbfile.acquisition["test_timeseries"])
    print(read_nwbfile.acquisition["test_timeseries"].data[:])

####################
# It is often preferable to read only a portion of the data.
# To do this, index or slice into the ``data`` attribute just like you
# index or slice a numpy array.

with NWBHDF5IO("basics_tutorial.nwb", "r") as io:
    read_nwbfile = io.read()
    print(read_nwbfile.acquisition["test_timeseries"].data[:2])

####################
# .. note::
#     If you use :py:class:`~pynwb.NWBHDF5IO` as a context manager during read,
#     be aware that the :py:class:`~pynwb.NWBHDF5IO` gets closed and when the
#     context completes and the data will not be available outside of the
#     context manager [#]_.

####################
# Accessing data
# ^^^^^^^^^^^^^^^
#
# We can also access the :py:class:`~pynwb.behavior.SpatialSeries` data by referencing the names
# of the objects in the hierarchy that contain it. We can access a processing module by indexing
# ``nwbfile.processing`` with the name of the processing module, ``"behavior"``.
#
# Then, we can access the :py:class:`~pynwb.behavior.Position` object inside of the ``"behavior"``
# processing module by indexing it with the name of the :py:class:`~pynwb.behavior.Position` object,
# ``"Position"``.
#
# Finally, we can access the :py:class:`~pynwb.behavior.SpatialSeries` object inside of the
# :py:class:`~pynwb.behavior.Position` object by indexing it with the name of the
# :py:class:`~pynwb.behavior.SpatialSeries` object, ``"SpatialSeries"``.

with NWBHDF5IO("basics_tutorial.nwb", "r") as io:
    read_nwbfile = io.read()
    print(read_nwbfile.processing["behavior"])
    print(read_nwbfile.processing["behavior"]["Position"])
    print(read_nwbfile.processing["behavior"]["Position"]["SpatialSeries"])

####################
# .. _basic_appending:
#
# Appending to an NWB file
# ------------------------
#
# To append to a file, read it with :py:class:`~pynwb.NWBHDF5IO` and set the ``mode`` argument to ``'a'``.
# After you have read the file, you can add [#]_ new data to it using the standard write/add functionality demonstrated
# above. Let's see how this works by adding another :py:class:`~pynwb.base.TimeSeries` to acquisition.

io = NWBHDF5IO("basics_tutorial.nwb", mode="a")
nwbfile = io.read()

data = np.arange(100, 200, 10)
timestamps = np.arange(10.)
new_time_series = TimeSeries(
    name="new_time_series",
    description="a new time series",
    data=data,
    timestamps=timestamps,
    unit="n.a.",
)
nwbfile.add_acquisition(new_time_series)

####################
# Finally, write the changes back to the file and close it.

io.write(nwbfile)
io.close()

####################
# .. [#] Some data interface objects have a default name. This default name is the type of the data interface. For
#    example, the default name for :py:class:`~pynwb.ophys.ImageSegmentation` is "ImageSegmentation" and the default
#    name for :py:class:`~pynwb.ecephys.EventWaveform` is "EventWaveform".
#
# .. [#] HDF5 is the primary backend supported by NWB.
#
# .. [#] Neurodata sets can be *very* large, so individual components of the dataset are only loaded into memory when
#    you request them. This functionality is only possible if an open file handle is kept around until users want to
#    load data.
#
# .. [#] NWB only supports *adding* to files. Removal and modifying of existing data is not allowed.
