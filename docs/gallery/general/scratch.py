"""
.. _scratch:

Exploratory Data Analysis with NWB
==================================

This example will focus on the basics of working with an :py:class:`~pynwb.file.NWBFile` to do more than
storing standardized data for use and exchange. For example, you may want to store results from intermediate
analyses or one-off analyses with unknown utility. This functionality is primarily accomplished with linking
and scratch space.


.. note::
    The scratch space is explicitly for non-standardized data that is not intended for reuse
    by others. Standard NWB types, and extension if required, should always be used for any data that you
    intend to share. As such, published data should not include scratch data and a user should be able
    to ignore any data stored in scratch to use a file.



"""

####################
# Raw data
# --------
#
# To demonstrate linking and scratch space, lets assume we are starting with some acquired data.
#

from datetime import datetime

import numpy as np
from dateutil.tz import tzlocal

# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_scratch.png'
from pynwb import NWBHDF5IO, NWBFile, TimeSeries

# set up the NWBFile
start_time = datetime(2019, 4, 3, 11, tzinfo=tzlocal())
create_date = datetime(2019, 4, 15, 12, tzinfo=tzlocal())

nwb = NWBFile(
    session_description="demonstrate NWBFile scratch",  # required
    identifier="NWB456",  # required
    session_start_time=start_time,  # required
    file_create_date=create_date,
)  # optional

# make some fake data
timestamps = np.linspace(0, 100, 1024)
data = (
    np.sin(0.333 * timestamps)
    + np.cos(0.1 * timestamps)
    + np.random.randn(len(timestamps))
)
test_ts = TimeSeries(name="raw_timeseries", data=data, unit="m", timestamps=timestamps)

# add it to the NWBFile
nwb.add_acquisition(test_ts)

with NWBHDF5IO("raw_data.nwb", mode="w") as io:
    io.write(nwb)

####################
# .. _basic_copying:
#
# Copying an NWB file
# -------------------
#
# To copy a file, we must first read the file.
#
raw_io = NWBHDF5IO("raw_data.nwb", "r")
nwb_in = raw_io.read()

####################
# And then create a shallow copy the file with the :py:func:`~pynwb.file.NWBFile.copy` method
# of :py:class:`~pynwb.file.NWBFile` .

nwb_proc = nwb_in.copy()

####################
#
# Now that we have a copy, lets process some data, and add the results as a :py:class:`~pynwb.base.ProcessingModule`
# to our copy of the file. [#]_

import scipy.signal as sps

mod = nwb_proc.create_processing_module(
    "filtering_module", "a module to store filtering results"
)

ts1 = nwb_in.acquisition["raw_timeseries"]
filt_data = sps.correlate(ts1.data, np.ones(128), mode="same") / 128
ts2 = TimeSeries(name="filtered_timeseries", data=filt_data, unit="m", timestamps=ts1)

mod.add_container(ts2)


####################
#
# Now write the copy, which contains the processed data. [#]_

with NWBHDF5IO("processed_data.nwb", mode="w", manager=raw_io.manager) as io:
    io.write(nwb_proc)


####################
#
# .. [#]
#    .. note::
#       Notice here that we are reusing the timestamps to the original TimeSeries.
#
# .. [#]
#    .. note::
#       The ``processed_data.nwb`` file (i.e., our copy) stores our processing module and contains external
#       links to all data in our original file, i.e., the data from our raw file is being linked to, not copied.
#       This allows us to isolate our processing data in a separate file while still allowing us to access the
#       raw data from our ``processed_data.nwb`` file, without having to duplicate the data.
#


####################
# .. _basic_scratch:
#
# Adding scratch data
# -------------------
#
# You may end up wanting to store results from some one-off analysis, and writing an extension
# to get your data into an NWBFile is too much over head. This is facilitated by the scratch space
# in NWB. [#]_
#
# First, lets read our processed data and then make a copy

proc_io = NWBHDF5IO("processed_data.nwb", "r")
nwb_proc_in = proc_io.read()

####################
#
# Now make a copy to put our scratch data into [#]_

nwb_scratch = nwb_proc_in.copy()

####################
#
# Now lets do an analysis for which we do not have a specification, but we would like to store
# the results for.

filt_ts = nwb_scratch.modules["filtering_module"]["filtered_timeseries"]

fft = np.fft.fft(filt_ts.data)

nwb_scratch.add_scratch(
    fft,
    name="dft_filtered",
    description="discrete Fourier transform from filtered data",
)


####################
#
# Finally, write the results.

with NWBHDF5IO("scratch_analysis.nwb", "w", manager=proc_io.manager) as io:
    io.write(nwb_scratch)

####################
#
# To get your results back, you can index into :py:attr:`~pynwb.file.NWBFile.scratch` or use
# :py:func:`~pynwb.file.NWBFile.get_scratch`:

scratch_io = NWBHDF5IO("scratch_analysis.nwb", "r")
nwb_scratch_in = scratch_io.read()

fft_in = nwb_scratch_in.scratch["dft_filtered"]

fft_in = nwb_scratch_in.get_scratch("dft_filtered")

####################
#
# .. [#]
#    .. note::
#       This scratch space only exists if you add scratch data.
#
# .. [#]
#    .. note::
#       We recommend writing scratch data into copies of files only. This will make it easier to
#       isolate and discard scratch data and avoids updating files that store precious data.

# close the IO objects
raw_io.close()
proc_io.close()
scratch_io.close()
