"""
.. _time_intervals:

Annotating Time Intervals
=========================

Annotating events in time is a common need in neuroscience, e.g. to describes epochs, trials, and
invalid times during an experimental session. NWB supports annotation of time intervals via the
:py:class:`~pynwb.epoch.TimeIntervals` type. The :py:class:`~pynwb.epoch.TimeIntervals` type is
a :py:class:`~hdmf.common.table.DynamicTable` with the following columns:

1. `start_time` and `stop_time` describe the start and stop times of intervals as floating point offsets in seconds
   relative to the :py:meth:`~pynwb.file.NWBFile.timestamps_reference_time` of the file. In addition,
2. `tags` is an optional, indexed column used to associate user-defined string tags with intervals (0 or more tags per
   time interval)
3. `timeseries` is an optional, indexed :py:class:`~pynwb.base.TimeSeriesReferenceVectorData` column to map intervals
   directly to ranges in select, relevant :py:class:`~pynwb.base.TimeSeries` (0 or more per time interval)
4. as a :py:class:`~hdmf.common.table.DynamicTable` user may add additional columns to
   :py:meth:`~pynwb.epoch.TimeIntervals` via :py:meth:`~hdmf.common.table.DynamicTable.add_column`


.. hint:: :py:meth:`~pynwb.epoch.TimeIntervals` is intended for storing general annotations of time ranges.
          Depending on the application (e.g., when intervals are generated by data acquisition or automatic
          data processing), it can be useful to describe intervals (or instantaneous events) in time
          as :py:class:`~pynwb.base.TimeSeries`. NWB provides several types for this purposes, e.g.,
          :py:class:`~pynwb.misc.IntervalSeries`, :py:class:`~pynwb.behavior.BehavioralEpochs`,
          :py:class:`~pynwb.behavior.BehavioralEvents`, :py:class:`~pynwb.ecephys.EventDetection`, or
          :py:class:`~pynwb.ecephys.SpikeEventSeries`.

"""

####################
# Setup: Creating an example NWB file for the tutorial
# ----------------------------------------------------
#

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_timeintervals.png'
from datetime import datetime
from uuid import uuid4

import numpy as np
from dateutil.tz import tzlocal

from pynwb import NWBFile, TimeSeries

# create the NWBFile
nwbfile = NWBFile(
    session_description="my first synthetic recording",  # required
    identifier=str(uuid4()),  # required
    session_start_time=datetime(2017, 4, 3, 11, tzinfo=tzlocal()),  # required
    experimenter="Baggins, Bilbo",  # optional
    lab="Bag End Laboratory",  # optional
    institution="University of Middle Earth at the Shire",  # optional
    experiment_description="I went on an adventure with thirteen dwarves to reclaim vast treasures.",  # optional
    session_id="LONELYMTN",  # optional
)
# create some example TimeSeries
test_ts = TimeSeries(
    name="series1",
    data=np.arange(1000),
    unit="m",
    timestamps=np.linspace(0.5, 601, 1000),
)
rate_ts = TimeSeries(
    name="series2", data=np.arange(600), unit="V", starting_time=0.0, rate=1.0
)
# Add the TimeSeries to the file
nwbfile.add_acquisition(test_ts)
nwbfile.add_acquisition(rate_ts)

####################
# Adding Time Intervals to a NWBFile
# ----------------------------------
#
# NWB provides a set of pre-defined :py:class:`~pynwb.epoch.TimeIntervals`
# tables for :py:meth:`~pynwb.file.NWBFile.epochs`, :py:meth:`~pynwb.file.NWBFile.trials`, and
# :py:meth:`~pynwb.file.NWBFile.invalid_times`.
#
# .. _trials:
#
# Trials
# ^^^^^^
#
# Trials can be added to an NWB file using the methods :py:meth:`~pynwb.file.NWBFile.add_trial`
# By default, NWBFile only requires trial `start_time` and `stop_time`. The `tags` and `timeseries` are optional. For
# `timeseries` we only need to supply the :py:class:`~pynwb.base.TimeSeries`.
# PyNWB automatically calculates the corresponding index range (described by ``idx_start`` and ``count``) for
# the supplied  :py:class:`~pynwb.base.TimeSeries` based on the given ``start_time`` and ``stop_time`` and
# the :py:meth:`~pynwb.base.TimeSeries.timestamps` (or :py:class:`~pynwb.base.TimeSeries.starting_time`
# and :py:meth:`~pynwb.base.TimeSeries.rate`) of the given :py:class:`~pynwb.base.TimeSeries`.
#
# Additional columns can be added using :py:meth:`~pynwb.file.NWBFile.add_trial_column`. This method takes a name
# for the column and a description of what the column stores. You do not need to supply data
# type, as this will inferred. Once all columns have been added, trial data can be populated using
# :py:meth:`~pynwb.file.NWBFile.add_trial`.
#
# Lets add an additional column and some trial data with tags and timeseries references.

nwbfile.add_trial_column(name="stim", description="the visual stimuli during the trial")

nwbfile.add_trial(
    start_time=0.0,
    stop_time=2.0,
    stim="dog",
    tags=["animal"],
    timeseries=[test_ts, rate_ts],
)
nwbfile.add_trial(
    start_time=3.0,
    stop_time=5.0,
    stim="mountain",
    tags=["landscape"],
    timeseries=[test_ts, rate_ts],
)
nwbfile.add_trial(
    start_time=6.0,
    stop_time=8.0,
    stim="desert",
    tags=["landscape"],
    timeseries=[test_ts, rate_ts],
)
nwbfile.add_trial(
    start_time=9.0,
    stop_time=11.0,
    stim="tree",
    tags=["landscape", "plant"],
    timeseries=[test_ts, rate_ts],
)
nwbfile.add_trial(
    start_time=12.0,
    stop_time=14.0,
    stim="bird",
    tags=["animal"],
    timeseries=[test_ts, rate_ts],
)
nwbfile.add_trial(
    start_time=15.0,
    stop_time=17.0,
    stim="flower",
    tags=["animal"],
    timeseries=[test_ts, rate_ts],
)

####################
# Epochs
# ^^^^^^
#
# Similarly, epochs can be added to an NWB file using the method :py:meth:`~pynwb.file.NWBFile.add_epoch` and
# :py:meth:`~pynwb.file.NWBFile.add_epoch_column`.

nwbfile.add_epoch(
    2.0,
    4.0,
    ["first", "example"],
    [
        test_ts,
    ],
)
nwbfile.add_epoch(
    6.0,
    8.0,
    ["second", "example"],
    [
        test_ts,
    ],
)

####################
# Invalid Times
# ^^^^^^^^^^^^^
#
# Similarly, invalid times can be added using the method :py:meth:`~pynwb.file.NWBFile.add_invalid_time_interval` and
# :py:meth:`~pynwb.file.NWBFile.add_invalid_times_column`.

nwbfile.add_epoch(
    2.0,
    4.0,
    ["first", "example"],
    [
        test_ts,
    ],
)
nwbfile.add_epoch(
    6.0,
    8.0,
    ["second", "example"],
    [
        test_ts,
    ],
)

####################
# Custom Time Intervals
# ^^^^^^^^^^^^^^^^^^^^^
#
# To define custom, experiment-specific :py:class:`~pynwb.epoch.TimeIntervals` we can add them
# either: 1) when creating the :py:class:`~pynwb.file.NWBFile` by defining the
# ``intervals`` constructor argument or 2) via the
# :py:meth:`~pynwb.file.NWBFile.add_time_intervals` or :py:meth:`~pynwb.file.NWBFile.create_time_intervals`
# after the :py:class:`~pynwb.file.NWBFile` has been created.
#

from pynwb.epoch import TimeIntervals

sleep_stages = TimeIntervals(
    name="sleep_stages",
    description="intervals for each sleep stage as determined by EEG",
)

sleep_stages.add_column(name="stage", description="stage of sleep")
sleep_stages.add_column(name="confidence", description="confidence in stage (0-1)")

sleep_stages.add_row(start_time=0.3, stop_time=0.5, stage=1, confidence=0.5)
sleep_stages.add_row(start_time=0.7, stop_time=0.9, stage=2, confidence=0.99)
sleep_stages.add_row(start_time=1.3, stop_time=3.0, stage=3, confidence=0.7)

_ = nwbfile.add_time_intervals(sleep_stages)


####################
# Accessing Time Intervals
# ------------------------
#
# We can access the predefined :py:class:`~pynwb.epoch.TimeIntervals` tables via the corresponding
# :py:meth:`~pynwb.file.NWBFile.epochs`, :py:meth:`~pynwb.file.NWBFile.trials`, and
# :py:meth:`~pynwb.file.NWBFile.invalid_times` properties and for custom :py:class:`~pynwb.epoch.TimeIntervals`
# via the :py:meth:`~pynwb.file.NWBFile.get_time_intervals`  method. E.g.:

_ = nwbfile.intervals
_ = nwbfile.get_time_intervals("sleep_stages")


####################
# Like any :py:class:`~hdmf.common.table.DynamicTable`, we can conveniently convert any
# :py:class:`~pynwb.epoch.TimeIntervals` table to a ``pandas.DataFrame`` via
# :py:meth:`~hdmf.common.table.DynamicTable.to_dataframe`, such as:

nwbfile.trials.to_dataframe()

####################
# This approach makes it easy to query the data to, e.g., locate all time intervals within a certain time range

trials_df = nwbfile.trials.to_dataframe()
trials_df.query("(start_time > 2.0) & (stop_time < 9.0)")

####################
# Accessing referenced TimeSeries
# -------------------------------
#
# As mentioned earlier, the ``timeseries`` column is defined by a :py:class:`~pynwb.base.TimeSeriesReferenceVectorData`
# which stores references to the corresponding ranges in :py:class:`~pynwb.base.TimeSeries`. Individual references
# to :py:class:`~pynwb.base.TimeSeries` are described via :py:class:`~pynwb.base.TimeSeriesReference` tuples
# with the :py:class:`~pynwb.base.TimeSeriesReference.idx_start`, :py:class:`~pynwb.base.TimeSeriesReference.count`,
# and :py:class:`~pynwb.base.TimeSeriesReference.timeseries`.
# Using :py:class:`~pynwb.base.TimeSeriesReference` we can easily access the relevant
# :py:meth:`~pynwb.base.TimeSeriesReference.data` and :py:meth:`~pynwb.base.TimeSeriesReference.timestamps`
# for the corresponding time range from the :py:class:`~pynwb.base.TimeSeries`.

# Get a single example TimeSeriesReference from the trials table
example_tsr = nwbfile.trials["timeseries"][0][0]

# Get the data values from the timeseries. This is a shorthand for:
# _ = example_tsr.timeseries.data[example_tsr.idx_start: (example_tsr.idx_start + example_tsr.count)]
_ = example_tsr.data

# Get the timestamps. Timestamps are either loaded from the TimeSeries or
# computed from the starting_time and rate
example_tsr.timestamps

####################
# Using :py:class:`~pynwb.base.TimeSeriesReference.isvalid` we can further check if the reference is valid.
# A :py:class:`~pynwb.base.TimeSeriesReference` is defined as invalid if both
# :py:class:`~pynwb.base.TimeSeriesReference.idx_start`, :py:class:`~pynwb.base.TimeSeriesReference.count` are
# set to ``-1``. :py:class:`~pynwb.base.TimeSeriesReference.isvalid` further also checks that the indicated
# index range and types are valid, raising ``IndexError`` and ``TypeError`` respectively, if bad
# :py:class:`~pynwb.base.TimeSeriesReference.idx_start`, :py:class:`~pynwb.base.TimeSeriesReference.count` or
# :py:class:`~pynwb.base.TimeSeriesReference.timeseries` are found.

example_tsr.isvalid()

####################
# Adding TimeSeries references to other tables
# --------------------------------------------
#
# Since :py:class:`~pynwb.base.TimeSeriesReferenceVectorData` is a regular :py:class:`~hdmf.common.table.VectorData`
# type, we can use it to add references to intervals in :py:class:`~pynwb.base.TimeSeries` to any
# :py:class:`~hdmf.common.table.DynamicTable`. In the :py:class:`~pynwb.icephys.IntracellularRecordingsTable`, e.g.,
# it is used to reference the recording of the stimulus and response associated with a particular intracellular
# electrophysiology recording.
#


####################
# Reading/Writing TimeIntervals to file
# -------------------------------------
#
# Reading and writing the data is as usual:

from pynwb import NWBHDF5IO

# write the file
with NWBHDF5IO("example_timeintervals_file.nwb", "w") as io:
    io.write(nwbfile)
# read the file
with NWBHDF5IO("example_timeintervals_file.nwb", "r") as io:
    nwbfile_in = io.read()

    # plot the sleep stages TimeIntervals table
    nwbfile_in.get_time_intervals("sleep_stages").to_dataframe()
