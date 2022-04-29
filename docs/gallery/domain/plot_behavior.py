"""
.. _behavior_basics:

Behavior Data
==================================

This tutorial will demonstrate the usage of the :py:class:`~pynwb.behavior` module for adding
behavior data to an :py:class:`~pynwb.file.NWBFile`.

An :py:class:`~pynwb.file.NWBFile` represents a single session of an experiment.
It contains all the data of that session and the metadata required to understand the data.


.. seealso::
    You can learn more about the :py:class:`~pynwb.file.NWBFile` format in the :ref:`basics` tutorial.


The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
"""
from datetime import datetime

import numpy as np
from dateutil import tz
from pynwb.misc import IntervalSeries

from pynwb.epoch import TimeIntervals

from pynwb import NWBFile, TimeSeries, NWBHDF5IO
from pynwb.behavior import (
    SpatialSeries,
    BehavioralTimeSeries,
    Position,
    BehavioralEvents,
    CompassDirection,
    BehavioralEpochs,
    PupilTracking,
    EyeTracking,
)

####################
# Create an NWB File
# ------------
#
# Create an :py:class:`~pynwb.file.NWBFile` object with the required fields
# (``session_description``, ``identifier``, ``session_start_time``) and additional metadata.

session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))

nwbfile = NWBFile(
    session_description="Mouse exploring an open field",  # required
    identifier="Mouse5_Day3",  # required
    session_start_time=session_start_time,  # required
    session_id="session_1234",  # optional
    experimenter="My Name",  # optional
    lab="My Lab Name",  # optional
    institution="University of My Institution",  # optional
    related_publications="DOI:10.1016/j.neuron.2016.12.011",  # optional
)

nwbfile

####################
# Position
# ------------
#
# Spatial Series
# ^^^^^^^^^^^^^^^
#
# :py:class:`~pynwb.behavior.SpatialSeries` is a subclass of :py:class:`~pynwb.base.TimeSeries`
# that represents the spatial direction, e.g., of gaze or travel, or position of an animal over time.
#
# .. seealso::
#    You can learn more about the :py:class:`~pynwb.behavior.SpatialSeries` data type and
#    :py:class:`~pynwb.behavior.Position` interface in the :ref:`basic_spatialseries` tutorial.
#
# Create data that corresponds to x, y position over time.

position_data = np.array([np.linspace(0, 10, 50), np.linspace(0, 8, 50)]).T

position_data.shape

####################
# In :py:class:`~pynwb.behavior.SpatialSeries` ``data``, the first dimension is always time (in seconds),
# the second dimension represents the x, y position (in meters).
#
# .. note::
#    :py:class:`~pynwb.behavior.SpatialSeries` data should be stored as one continuous stream,
#    as it is acquired, not by trial as is often reshaped for analysis.
#    Data can be trial-aligned on-the-fly using the trials table. See the :ref:`basic_trials` tutorial
#    for further information.
#
# For position data ``reference_frame`` indicates the zero-position, e.g.
# the 0,0 point might be the bottom-left corner of an enclosure, as viewed from the tracking camera.

timestamps = np.linspace(0, 50) / 200

position_spatial_series = SpatialSeries(
    name="SpatialSeries",
    description="(x,y) position in open field",
    data=position_data,
    timestamps=timestamps,
    reference_frame="(0,0) is bottom left corner",
)

position_spatial_series

####################
#
# .. seealso::
#    You can learn more about best practices that can be applied to
#    :py:class:`~pynwb.behavior.SpatialSeries` `here <https://www.nwb.org/best-practices/#timeseries>`_.
#
# To help data analysis and visualization tools know that this :py:class:`~pynwb.behavior.SpatialSeries` object
# represents the position of the subject, store the :py:class:`~pynwb.behavior.SpatialSeries` object inside
# of a :py:class:`~pynwb.behavior.Position` object, which can hold one or more :py:class:`~pynwb.behavior.SpatialSeries` objects.

position = Position(spatial_series=position_spatial_series)


####################
# Create a Behavior Processing Module
# --------------------------
#
# .. seealso::
#    You can read more about the basic concepts of processing modules in the :ref:`modules_overview` tutorial.
#
# Create a processing module called ``"behavior"`` for storing behavioral data in the :py:class:`~pynwb.file.NWBFile`
# and add the :py:class:`~pynwb.behavior.Position` object to the processing module using the
# :py:meth:`~pynwb.file.NWBFile.create_processing_module` method:


behavior_module = nwbfile.create_processing_module(
    name="behavior", description="processed behavioral data"
)

behavior_module.add(position)


####################
# CompassDirection
# ------------
#
# Spatial Series
# ^^^^^^^^^^^^^^^
#
# Analogous to how position can be stored, we can create a :py:class:`~pynwb.behavior.SpatialSeries`
# object for representing the view angle of the subject.
#
# For direction data ``reference_frame`` indicates the zero-axes, for instance
# “straight-ahead” might be a specific pixel on the monitor, or some other point in space.
# The unit of measurement for the :py:class:`~pynwb.behavior.SpatialSeries` object should be radians or degrees.

view_angle_data = np.linspace(0, 4, 50)

direction_spatial_series = SpatialSeries(
    name="SpatialSeries",
    description="view angle",
    data=view_angle_data,
    timestamps=timestamps,
    reference_frame="bottom left",
    unit="radians",
)

direction = CompassDirection(
    spatial_series=direction_spatial_series, name="CompassDirection"
)

####################
# We can add a :py:class:`~pynwb.behavior.CompassDirection` object to the ``behavior`` processing module
# the same way as we have added the position data:

behavior_module.add(direction)


####################
# BehavioralTimeSeries
# ------------
#
# :py:class:`~pynwb.behavior.BehavioralTimeSeries` is an interface for storing continuous behavior data.
# Create a :py:class:`~pynwb.base.TimeSeries` object that represents the speed/velocity of an animal.

speed_data = np.linspace(0, 0.4, 50)

speed_time_series = TimeSeries(
    name="speed",
    data=speed_data,
    timestamps=timestamps,
    unit="m/s",
)

behavioral_time_series = BehavioralTimeSeries(
    time_series=speed_time_series,
    name="BehavioralTimeSeries",
)

####################
# BehavioralEvents
# ------------
#
# :py:class:`~pynwb.behavior.BehavioralEvents` is an interface for storing behavioral events.
# We can use it for storing the amount of reward (e.g. water amount) - floats
# or duration of stimulus (floats of timestamps) happened irregularly
# Create a :py:class:`~pynwb.base.TimeSeries` object that represents the speed/velocity of an animal.

data = np.full(50, np.nan)
duration_of_stimulus = np.ones(10, dtype=float)
data[::5] = duration_of_stimulus

events_timestamps = np.full(50, np.nan)
events_timestamps[::5] = timestamps[np.where(~np.isnan(data))]

time_series = TimeSeries(
    name="stimulus_duration",
    data=data,
    timestamps=events_timestamps,
    unit="seconds",
)

behavioral_events = BehavioralEvents(time_series=time_series, name="BehavioralEvents")

####################
# BehavioralEpochs
# ------------
# :py:class:`~pynwb.behavior.BehavioralEpochs` is for storing intervals of behavior data.
# :py:class:`~pynwb.behavior.BehavioralEpochs` uses :py:class:`~pynwb.misc.IntervalSeries`
# to represent behavioral epochs.
#
# Create :py:class:`~pynwb.misc.IntervalSeries` object that represents the time intervals
# when the animal was running.


run_intervals_1 = IntervalSeries(
    name="run_intervals_1",
    description="intervals when the animal was running",
    data=np.arange(6, 18, 1),
    timestamps=np.arange(6, 18, 1).astype(float),
)

run_intervals_2 = IntervalSeries(
    name="run_intervals_2",
    description="intervals when the animal was running",
    data=np.arange(22, 34, 1),
    timestamps=np.arange(22, 34, 1).astype(float),
)

behavioral_epochs = BehavioralEpochs(name="BehavioralEpochs")

behavioral_epochs.add_interval_series(run_intervals_1)
behavioral_epochs.add_interval_series(run_intervals_2)

####################
# Using :py:class:`~pynwb.epoch.TimeIntervals` representing time intervals
# is preferred over :py:class:`~pynwb.behavior.BehavioralEpochs`.
# :py:class:`~pynwb.epoch.TimeIntervals` is a subclass of :py:class:`~pynwb.core.DynamicTable`
# which offers flexibility for tabular data by allowing the addition of optional columns
# which are not defined in the standard.
#
# Create a :py:class:`~pynwb.epoch.TimeIntervals` object that represents the time
# intervals when the animal was sleeping.

sleep_intervals = TimeIntervals(
    name="sleep_intervals",
    description="intervals when the animal was sleeping",
)

sleep_intervals.add_column(name="stage", description="stage of sleep")

sleep_intervals.add_row(start_time=0.3, stop_time=0.35, stage=1)
sleep_intervals.add_row(start_time=0.7, stop_time=0.9, stage=2)
sleep_intervals.add_row(start_time=1.3, stop_time=3.0, stage=3)

nwbfile.add_time_intervals(sleep_intervals)

####################
# Analogous to how position and direction data can be added to the ``behavior`` processing module,
# we can add the other behavior data:

behavior_module.add(behavioral_time_series)
behavior_module.add(behavioral_events)
behavior_module.add(behavioral_epochs)


####################
# PupilTracking
# --------------------------
#
# :py:class:`~pynwb.behavior.PupilTracking` is for storing eye-tracking data which
# represents pupil size. :py:class:`~pynwb.behavior.PupilTracking` holds one or more
# :py:class:`~pynwb.base.TimeSeries` objects that can represent different features
# such as the dilation of the pupil measured over time by a pupil tracking algorithm.
#

pupil_diameter = TimeSeries(
    name="pupil_diameter",
    description="pupil diameter extracted from the video of the right eye",
    data=np.linspace(0.001, 0.002, 50),
    timestamps=timestamps,
    unit="meters",
)


pupil_tracking = PupilTracking(time_series=pupil_diameter, name="PupilTracking")

####################
# We can add a :py:class:`~pynwb.behavior.PupilTracking` object to the ``behavior``
# processing module the same way as we have added the other data types.

behavior_module.add(pupil_tracking)

####################
# EyeTracking
# --------------------------
#
# :py:class:`~pynwb.behavior.EyeTracking` is for storing eye-tracking data which
# represents direction of gaze as measured by an eye tracking algorithm.
# An :py:class:`~pynwb.behavior.EyeTracking` object holds one or more
# :py:class:`~pynwb.behavior.SpatialSeries` objects that represents spatial features
# such as the vertical and horizontal gaze positions extracted from a video.
#

right_eye_position = np.linspace(-20, 30, 50)

right_eye_positions = SpatialSeries(
    name="right_eye_position",
    description="position of the right eye",
    data=right_eye_position,
    timestamps=timestamps,
    reference_frame="bottom left",
    unit="degrees",
)

eye_tracking = EyeTracking(name="EyeTracking", spatial_series=right_eye_positions)

####################
# We can add another :py:class:`~pynwb.behavior.SpatialSeries` representing the position
# of the left eye in degrees.

left_eye_position = np.linspace(-2, 20, 50)

left_eye_positions = SpatialSeries(
    name="left_eye_position",
    description="position of the left eye",
    data=left_eye_position,
    timestamps=timestamps,
    reference_frame="bottom left",
    unit="degrees",
)

eye_tracking.add_spatial_series(spatial_series=left_eye_positions)

####################
# We can add an :py:class:`~pynwb.behavior.EyeTracking` object to the ``behavior``
# processing module the same way as we have added the other data types.

behavior_module.add(eye_tracking)


####################
# Writing the behavior data to an NWB file
# -------------------
#
# As demonstrated in the :ref:`basic_writing` tutorial, we will use :py:class:`~pynwb.NWBHDF5IO`
# to write the file.

with NWBHDF5IO("behavioral_tutorial.nwb", "w") as io:
    io.write(nwbfile)

####################
# Reading and accessing the behavior data
# -------------------
#
# To read the NWB file we just wrote, use another :py:class:`~pynwb.NWBHDF5IO` object,
# and use the :py:meth:`~pynwb.NWBHDF5IO.read` method to retrieve an
# :py:class:`~pynwb.file.NWBFile` object.
#
# We can access the behavior processing module by indexing ``nwbfile.processing``
# with the name of the processing module ``"behavior"``. We can also inspect the objects
# hierarchy within this processing module with the ``.children`` attribute.

with NWBHDF5IO("behavioral_tutorial.nwb", "r") as io:
    read_nwbfile = io.read()
    print(read_nwbfile.processing["behavior"].children)

####################
# For instance, we can access the :py:class:`~pynwb.behavior.SpatialSeries` data
# by referencing the names of the objects in the hierarchy that contain it.
# We can access the :py:class:`~pynwb.behavior.Position` object inside of the ``behavior``
# processing module by indexing it with the name of the :py:class:`~pynwb.behavior.Position` object,
# ``"Position"``. Then, we can access the :py:class:`~pynwb.behavior.SpatialSeries` object inside of the
# :py:class:`~pynwb.behavior.Position` object by indexing it with the name of the
# :py:class:`~pynwb.behavior.SpatialSeries` object, ``"SpatialSeries"``.


with NWBHDF5IO("behavioral_tutorial.nwb", "r") as io:
    read_nwbfile = io.read()
    print(read_nwbfile.processing["behavior"]["Position"]["SpatialSeries"])

####################
# Data arrays are read passively from the file.
# Accessing the ``data`` attribute of the :py:class:`~pynwb.behavior.SpatialSeries` object
# does not read the data values, but presents an HDF5 object that can be indexed to read data.
# You can use the ``[:]`` operator to read the entire data array into memory.

with NWBHDF5IO("behavioral_tutorial.nwb", "r") as io:
    read_nwbfile = io.read()
    print(read_nwbfile.processing["behavior"]["Position"]["SpatialSeries"].data[:])

####################
# Alternatively, you can read only a portion of the data by indexing or slicing into
# the ``data`` attribute just like if you were indexing or slicing a numpy array.

with NWBHDF5IO("behavioral_tutorial.nwb", "r") as io:
    read_nwbfile = io.read()
    print(read_nwbfile.processing["behavior"]["Position"]["SpatialSeries"].data[:2])
