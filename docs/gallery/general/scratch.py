"""
.. _scratch:

Exploratory data analysis with NWB
==================================

This example will focus on the basics of working with an :py:class:`~pynwb.file.NWBFile` to do more than
convert data for exchange. For example, you may want to store results from intermediate analyses or one-off
analyses with unknown utility. This functionality is primarily accomplished with linking and scratch space.



"""

####################
# Raw data
# --------
#
# To demonstrate linking and scratch space, lets assume we are starting with some acquired data.
#

from pynwb import NWBFile, TimeSeries, NWBHDF5IO
from datetime import datetime
from dateutil.tz import tzlocal
import numpy as np

# set up the NWBFile
start_time = datetime(2019, 4, 3, 11, tzinfo=tzlocal())
create_date = datetime(2019, 4, 15, 12, tzinfo=tzlocal())

nwb = NWBFile(session_description='demonstrate NWBFile scratch',  # required
                  identifier='NWB456',  # required
                  session_start_time=start_time,  # required
                  file_create_date=create_date)  # optional

# make some fake data
timestamps = np.linspace(0, 100, 1024)
data = np.sin(0.333*timestamps) + np.cos(0.1*timestamps) + np.random.randn(len(timestamps))
test_ts = TimeSeries(name='raw_timeseries', data=data, unit='m', timestamps=timestamps)

# add it to the NWBFile
nwb.add_acquisition(test_ts)

with NWBHDF5IO('raw_data.nwb', mode='w') as io:
    io.write(nwb)

####################
# .. _basic_copying:
#
# Copying an NWB file
# -------------------
#
# To copy a file, the file must first be read.
#
raw_io = NWBHDF5IO('raw_data.nwb', 'r')
nwb_in = raw_io.read()

####################
# And then copy the file with NWBFile.copy

nwb_proc = nwb_in.copy()

####################
#
# Now that we have a copy, lets process some data, and add the results back into a ProcessingModule

import scipy.signal as sps

mod = nwb_proc.create_processing_module('filtering_module', "a module to store filtering results")

ts1 = nwb_in.acquisition['raw_timeseries']
filt_data = sps.correlate(ts1.data, np.ones(128), mode='same')/128
ts2 = TimeSeries(name='filtered_timeseries', data=filt_data, unit='m', timestamps=ts1)

mod.add_container(ts2)


####################
#
# Now write the copy, which contains processed data.

with NWBHDF5IO('processed_data.nwb', mode='w', manager=raw_io.manager) as io:
    io.write(nwb_proc)



####################
#
# .. note::
#    Notice here that we are reusing the timestamps to the original TimeSeries.


####################
# .. _basic_scratch:
#
# Adding scratch data
# -------------------
#
# You may end up wanting to store results from some one-off analysis, and writing an extension
# to get your data into an NWBFile is too much over head. This is faciliated by the scratch space
# in NWB. [#]_
#
# First, lets read our processed data and then make a copy

proc_io = NWBHDF5IO('processed_data.nwb', 'r')
nwb_proc_in = proc_io.read()


####################
#
# Now make a copy to put our scratch data into [#]_


nwb_scratch  = nwb_proc_in.copy()

####################
#
# Now lets do an analysis for which we do not have a specification, but we would like to store
# the results for.

filt_ts = nwb_scratch.modules['filtering_module']['filtered_timeseries']

fft = np.fft.fft(filt_ts.data)

nwb_scratch.add_scratch(fft, name='dft_filtered', notes='discrete Fourier transform from filtered data')


####################
#
# Finally, write the results.

with NWBHDF5IO('scratch_analysis.nwb', 'w', manager=proc_io.manager) as io:
    io.write(nwb_scratch)


####################
# .. [#] This scratch space only exists if you add scratch data.
#
# .. [#] We recommend writing scratch data into copyies only. This will make it easier to
#        discard data.
