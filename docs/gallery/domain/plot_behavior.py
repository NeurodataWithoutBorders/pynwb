"""
.. _behavior_basics:

Behavior Data
==================================

This tutorial will demonstrate how to add basic behavior data to an NWB File.

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

from pynwb import NWBFile, TimeSeries
from pynwb.behavior import (
    SpatialSeries,
    BehavioralTimeSeries,
    Position,
    BehavioralEvents,
    CompassDirection,
    BehavioralEpochs,
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
# TODO
# mention compression of data, timestamps with H5DataIO
# H5DataIO(timestamps, compression="gzip")


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
    data=np.arange(6.12, 18.36, 0.2),
    timestamps=np.arange(6.12, 18.36, 0.2),
)

run_intervals_2 = IntervalSeries(
    name="run_intervals_2",
    description="intervals when the animal was running",
    data=np.arange(6.12, 18.36, 0.2),
    timestamps=np.arange(6.12, 18.36, 0.2),
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
# Analogous to how position can be added to the ``behavior`` processing module,
# we can add the other behavior data:

behavior_module.add(direction)
behavior_module.add(behavioral_time_series)
behavior_module.add(behavioral_events)
behavior_module.add(behavioral_epochs)

####################
# Writing the file
# TODO
# Reading the file
# TODO
# Access the data
