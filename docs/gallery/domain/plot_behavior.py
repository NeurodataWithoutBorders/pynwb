"""
.. _behavior_basics:

Behavior Data
==================================

This tutorial will demonstrate the usage of the :py:mod:`pynwb.behavior` module for adding
behavioral data to an :py:class:`~pynwb.file.NWBFile`.

.. seealso::
    You can learn more about the :py:class:`~pynwb.file.NWBFile` format in the :ref:`basics` tutorial.

The examples below follow this general workflow for adding behavior data to an :py:class:`~pynwb.file.NWBFile`:

* create an object:

  * :py:class:`~pynwb.base.TimeSeries` for continuous time series data,
  * :py:class:`~pynwb.behavior.SpatialSeries` for continuous spatial data (e.g. position, direction relative to some
    reference frame),
  * :py:class:`~pynwb.misc.IntervalSeries` or :py:class:`~pynwb.epoch.TimeIntervals` for time intervals

* store that object inside a behavior interface object:

  * :py:class:`~pynwb.behavior.Position` for position measured over time
  * :py:class:`~pynwb.behavior.CompassDirection` for view angle measured over time
  * :py:class:`~pynwb.behavior.BehavioralTimeSeries` for continuous time series data
  * :py:class:`~pynwb.behavior.BehavioralEvents` for behavioral events (e.g. reward amount)
  * :py:class:`~pynwb.behavior.BehavioralEpochs` for behavioral intervals (e.g. sleep intervals)
  * :py:class:`~pynwb.behavior.PupilTracking` for eye-tracking data of pupil size
  * :py:class:`~pynwb.behavior.EyeTracking` for eye-tracking data of gaze direction

* create a behavior processing module for the :py:class:`~pynwb.file.NWBFile` and add the interface object(s) to it


The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
"""
# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_behavior.png'

from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil.tz import tzlocal

from pynwb import NWBHDF5IO, NWBFile, TimeSeries
from pynwb.behavior import (
    BehavioralEpochs,
    BehavioralEvents,
    BehavioralTimeSeries,
    CompassDirection,
    EyeTracking,
    Position,
    PupilTracking,
    SpatialSeries,
)
from pynwb.epoch import TimeIntervals
from pynwb.misc import IntervalSeries

####################
# Create an NWB File
# ------------------
#
# Create an :py:class:`~pynwb.file.NWBFile` object with the required fields
# (``session_description``, ``identifier``, ``session_start_time``) and additional metadata.

nwbfile = NWBFile(
    session_description="my first synthetic recording",
    identifier=str(uuid4()),
    session_start_time=datetime.now(tzlocal()),
    experimenter=[
        "Baggins, Bilbo",
    ],
    lab="Bag End Laboratory",
    institution="University of Middle Earth at the Shire",
    experiment_description="I went on an adventure to reclaim vast treasures.",
    session_id="LONELYMTN001",
)

nwbfile

####################
# SpatialSeries: Storing continuous spatial data
# ----------------------------------------------
#
# :py:class:`~pynwb.behavior.SpatialSeries` is a subclass of :py:class:`~pynwb.base.TimeSeries`
# that represents data in space, such as the spatial direction, e.g., of gaze or travel,
# or position of an animal over time.
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
#    Data can be trial-aligned on-the-fly using the trials table. See the :ref:`time_intervals` tutorial
#    for further information.
#
# For position data ``reference_frame`` indicates the zero-position, e.g.
# the 0,0 point might be the bottom-left corner of an enclosure, as viewed from the tracking camera.
# In :py:class:`~pynwb.behavior.SpatialSeries`, the ``bounds`` field allows the user to set
# the boundary range, i.e.,  (min, max), for each dimension of ``data``. The units are the same as in ``data``.
# This field does not enforce a boundary on the dataset itself.

timestamps = np.linspace(0, 50) / 200

position_spatial_series = SpatialSeries(
    name="SpatialSeries",
    description="Position (x, y) in an open field.",
    data=position_data,
    bounds=[(0,50), (0,50)],
    timestamps=timestamps,
    reference_frame="(0,0) is bottom left corner",
)

position_spatial_series

####################
# Position: Storing position measured over time
# ---------------------------------------------
#
# To help data analysis and visualization tools know that this :py:class:`~pynwb.behavior.SpatialSeries` object
# represents the position of the subject, store the :py:class:`~pynwb.behavior.SpatialSeries` object inside
# a :py:class:`~pynwb.behavior.Position` object, which can hold one or more :py:class:`~pynwb.behavior.SpatialSeries`
# objects.

position = Position(spatial_series=position_spatial_series)

####################
#
# .. seealso::
#    You can learn more about the :py:class:`~pynwb.behavior.SpatialSeries` data type and
#    :py:class:`~pynwb.behavior.Position` interface in the :ref:`basic_spatialseries` tutorial.
#
# .. seealso::
#    You can learn more about best practices that can be applied to
#    :py:class:`~pynwb.behavior.SpatialSeries` at `NWB Best Practices
#    <https://nwbinspector.readthedocs.io/en/dev/best_practices/time_series.html>`_.
#

####################
# Create a Behavior Processing Module
# -----------------------------------
#
# Create a processing module called ``"behavior"`` for storing behavioral data in the :py:class:`~pynwb.file.NWBFile`
# using the :py:meth:`~pynwb.file.NWBFile.create_processing_module` method, and then add the
# :py:class:`~pynwb.behavior.Position` object to the processing module.


behavior_module = nwbfile.create_processing_module(
    name="behavior", description="Processed behavioral data"
)

behavior_module.add(position)

####################
# .. seealso::
#    You can read more about the basic concepts of processing modules in the :ref:`modules_overview` tutorial.
#

####################
# CompassDirection: Storing view angle measured over time
# -------------------------------------------------------
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
    description="View angle of the subject measured in radians.",
    data=view_angle_data,
    timestamps=timestamps,
    reference_frame="straight ahead",
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
# BehavioralTimeSeries: Storing continuous behavior data
# ------------------------------------------------------
#
# :py:class:`~pynwb.behavior.BehavioralTimeSeries` is an interface for storing continuous behavior data, such as the
# speed of a subject.

speed_data = np.linspace(0, 0.4, 50)

speed_time_series = TimeSeries(
    name="speed",
    data=speed_data,
    timestamps=timestamps,
    description="The speed of the subject measured over time.",
    unit="m/s",
)

behavioral_time_series = BehavioralTimeSeries(
    time_series=speed_time_series,
    name="BehavioralTimeSeries",
)

behavior_module.add(behavioral_time_series)

####################
# BehavioralEvents: Storing behavioral events
# -------------------------------------------
#
# :py:class:`~pynwb.behavior.BehavioralEvents` is an interface for storing behavioral events.
# We can use it for storing the timing and amount of rewards (e.g. water amount) or lever press times.

reward_amount = [1.0, 1.5, 1.0, 1.5]
events_timestamps = [1.0, 2.0, 5.0, 6.0]

time_series = TimeSeries(
    name="lever_presses",
    data=reward_amount,
    timestamps=events_timestamps,
    description="The water amount the subject received as a reward.",
    unit="ml",
)

behavioral_events = BehavioralEvents(time_series=time_series, name="BehavioralEvents")

behavior_module.add(behavioral_events)

####################
# Storing only the timestamps of the events is possible with the `ndx-events <https://pypi.org/project/ndx-events/>`_
# NWB extension. You can also add labels associated with the events with this extension.
# You can find information about installation and example usage :nwb_extension:`here <ndx-events-record>`.
#
# .. seealso::
#    You can learn more about using extensions in the :ref:`tutorial-extending-nwb` tutorial.

####################
# BehavioralEpochs: Storing intervals of behavior data
# ----------------------------------------------------
# :py:class:`~pynwb.behavior.BehavioralEpochs` is for storing intervals of behavior data.
# :py:class:`~pynwb.behavior.BehavioralEpochs` uses :py:class:`~pynwb.misc.IntervalSeries`
# to represent behavioral epochs.
#
# Create :py:class:`~pynwb.misc.IntervalSeries` object that represents the time intervals
# when the animal was running. :py:class:`~pynwb.misc.IntervalSeries` uses 1 to indicate
# the beginning of an interval and -1 to indicate the end.


run_intervals = IntervalSeries(
    name="running",
    description="Intervals when the animal was running.",
    data=[1, -1, 1, -1, 1, -1],
    timestamps=[0.5, 1.5, 3.5, 4.0, 7.0, 7.3],
)

behavioral_epochs = BehavioralEpochs(name="BehavioralEpochs")

behavioral_epochs.add_interval_series(run_intervals)

####################
# you can add more than one :py:class:`~pynwb.misc.IntervalSeries` to a
# :py:class:`~pynwb.behavior.BehavioralEpochs`

sleep_intervals = IntervalSeries(
    name="sleeping",
    description="Intervals when the animal was sleeping.",
    data=[1, -1, 1, -1],
    timestamps=[15.0, 30.0, 60.0, 95.0],
)
behavioral_epochs.add_interval_series(sleep_intervals)

behavior_module.add(behavioral_epochs)

####################
# Using :py:class:`~pynwb.epoch.TimeIntervals` representing time intervals
# is often preferred over :py:class:`~pynwb.behavior.BehavioralEpochs` and :py:class:`~pynwb.misc.IntervalSeries`.
# :py:class:`~pynwb.epoch.TimeIntervals` is a subclass of :py:class:`~hdmf.common.table.DynamicTable` which offers
# flexibility for tabular data by allowing the addition of optional columns which are not defined in the standard.
#
# Create a :py:class:`~pynwb.epoch.TimeIntervals` object that represents the time
# intervals when the animal was sleeping.

sleep_intervals = TimeIntervals(
    name="sleep_intervals",
    description="Intervals when the animal was sleeping.",
)

sleep_intervals.add_column(name="stage", description="The stage of sleep.")

sleep_intervals.add_row(start_time=0.3, stop_time=0.35, stage=1)
sleep_intervals.add_row(start_time=0.7, stop_time=0.9, stage=2)
sleep_intervals.add_row(start_time=1.3, stop_time=3.0, stage=3)

nwbfile.add_time_intervals(sleep_intervals)


####################
# PupilTracking: Storing continuous eye-tracking data of pupil size
# -------------------------------------------------------------------
#
# :py:class:`~pynwb.behavior.PupilTracking` is for storing eye-tracking data which
# represents pupil size. :py:class:`~pynwb.behavior.PupilTracking` holds one or more
# :py:class:`~pynwb.base.TimeSeries` objects that can represent different features
# such as the dilation of the pupil measured over time by a pupil tracking algorithm.
#

pupil_diameter = TimeSeries(
    name="pupil_diameter",
    description="Pupil diameter extracted from the video of the right eye.",
    data=np.linspace(0.001, 0.002, 50),
    timestamps=timestamps,
    unit="meters",
)

pupil_tracking = PupilTracking(time_series=pupil_diameter, name="PupilTracking")

behavior_module.add(pupil_tracking)

####################
# EyeTracking: Storing continuous eye-tracking data of gaze direction
# -------------------------------------------------------------------
#
# :py:class:`~pynwb.behavior.EyeTracking` is for storing eye-tracking data which
# represents direction of gaze as measured by an eye tracking algorithm.
# An :py:class:`~pynwb.behavior.EyeTracking` object holds one or more
# :py:class:`~pynwb.behavior.SpatialSeries` objects that represents the vertical and
# horizontal gaze positions extracted from a video.

right_eye_position = np.linspace(-20, 30, 50)

right_eye_positions = SpatialSeries(
    name="right_eye_position",
    description="The position of the right eye measured in degrees.",
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
    description="The position of the left eye measured in degrees.",
    data=left_eye_position,
    timestamps=timestamps,
    reference_frame="bottom left",
    unit="degrees",
)

eye_tracking.add_spatial_series(spatial_series=left_eye_positions)

behavior_module.add(eye_tracking)


####################
# Writing the behavior data to an NWB file
# ----------------------------------------
#
# As demonstrated in the :ref:`basic_writing` tutorial, we will use :py:class:`~pynwb.NWBHDF5IO` to write the file.

with NWBHDF5IO("behavioral_tutorial.nwb", "w") as io:
    io.write(nwbfile)

####################
# Reading and accessing the behavior data
# ---------------------------------------
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
# We can access the :py:class:`~pynwb.behavior.Position` object inside the ``behavior``
# processing module by indexing it with the name of the :py:class:`~pynwb.behavior.Position` object,
# ``"Position"``. Then, we can access the :py:class:`~pynwb.behavior.SpatialSeries` object inside the
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
