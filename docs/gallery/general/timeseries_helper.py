"""
Working with TimeSeries
=======================

This example demonstrates the use of :class:`~pynwb.tools.tstools.TimeSeriesHelper` to facilitate selection of
data and plotting of TimeSeries data.

"""

####################
# Creating an example NWB:N file
# --------------------------------------------
#
# To demonstrate interaction with TimeSeries in a practical setting we here first create, write,
# and finally read an example NWB:N with a synthetic TimeSeries

from datetime import datetime
from pynwb import NWBFile

start_time = datetime(2018, 6, 12, 18, 7, 13, 0)
create_date = datetime.now()

nwbfile = NWBFile('PyNWB tutorial', 'demonstrate NWBFile basics', 'NWB123', start_time,
                  file_create_date=create_date)

####################
# Add an example TimeSeries to the file

from pynwb import TimeSeries
import numpy as np

data = np.sin(np.arange(1200).reshape(200, 2, 3) / 200. * np.pi  )
test_ts = TimeSeries(name='test_timeseries',
                     source='PyNWB tutorial',
                     data=data,
                     unit='SiUnit',
                     starting_time=0.,
                     rate=0.5)
nwbfile.add_acquisition(test_ts)

####################
# Write the file to disk

from pynwb import NWBHDF5IO

io = NWBHDF5IO('basic_subsetting_example.nwb', 'w')
io.write(nwbfile)
io.close()

####################
# Read the example NWB:N file back
#
inio =  NWBHDF5IO('basic_subsetting_example.nwb', 'r')
infile = inio.read()
intimeseries = infile.get_acquisition('test_timeseries')


####################
# Select a subset of a TimeSeries
# -----------------------------------------------------------
#

from pynwb.tools.tstools import TimeSeriesHelper

myseries_helper = TimeSeriesHelper(intimeseries)
subset_series = myseries_helper.subset_series(
    name='my_subset',
    time_range=(72.2, 80.5),  # Select time by start and stop range in seconds
    index_select=np.s_[:, 1,:])  # Select channels using index_based selection
print(type(subset_series))

####################
# ``[Out]:``
#
#  .. code-block:: python
#
#       <class 'pynwb.base.TimeSeries'>


####################
# .. note::
#
#    ``subset_series`` again creates a TimeSeries of the same type we selected from.
#    However, the new TimeSeries exists only in memory and has not been added to
#    an NWBFile.
#
# .. note::
#
#   ``subset_series`` currently loads the data into memory, rather than using a lazy
#   reference to the data.
#
# .. tip::
#
#     In ``index_select`` parameter the first part always refers to time. I.e.,
#     if we specify a time_range than the first selection of the index_select
#     should always be everything (i.e,. slice(None) or : when using np.s_)
#     as subset_series will define that part of the selection directly based
#     on the specified ``time_range``

####################
# Convert the TimeSeries to Pandas
# -----------------------------------------------------------
#

subset_series_helper = TimeSeriesHelper(subset_series)
df = subset_series_helper.to_pandas(use_absolute_times=False,
                                    session_start_time=infile.session_start_time)
print(df)

####################
# ``[Out]:``
#
#  .. code-block:: python
#
#                                                               0         1         2
#        Offset to session start at 2018-06-12 18:07:13
#        00:01:12                                        0.868632  0.876307  0.883766
#        00:01:17                                        0.911403  0.917755  0.923880
#        00:01:13                                        0.946085  0.951057  0.955793
#        00:01:18                                        0.972370  0.975917  0.979223
#        00:01:14                                        0.990024  0.992115  0.993961
#        00:01:19                                        0.998890  0.999507  0.999877
#        00:01:15                                        0.998890  0.998027  0.996917
#        00:01:20                                        0.990024  0.987688  0.985109
#        00:01:16                                        0.972370  0.968583  0.964557
#        00:01:21                                        0.946085  0.940881  0.935444
#        00:01:17                                        0.911403  0.904827  0.898028
#        00:01:22                                        0.868632  0.860742  0.852640
#        00:01:18                                        0.818150  0.809017  0.799685
#        00:01:23                                        0.760406  0.750111  0.739631
#        00:01:19                                        0.695913  0.684547  0.673013
#        00:01:24                                        0.625243  0.612907  0.600420
#        00:01:20                                        0.549023  0.535827  0.522499
#        00:01:25                                        0.467930  0.453990  0.439939
#

####################
# .. note::
#
#    The ``to_pandas`` function only converts the data and timestamps of the timeseries, i.e.,
#    it does not preserve any additional metadata available on the TimeSeries.

####################
# Plot the timeseries using Pandas
# -----------------------------------------------------------
# Plot the timeseries by converting it to pandas and then calling its plot function. We here vary how
# timestamps are converted to the index of the pandas dataframe i.e.: 1) using a TimedeltaIndex with
# unknown start, 2) using a TimedeltaIndex with known start, 3) using a DatetimeIndex of absolute times.

#%matplotlib inline   # Add this line when running in a notebook
from matplotlib import pyplot as plt

# Plot with just the time offsets
subset_series_helper.plot_pandas(figsize=(12,5))
plt.show()

# Plot with time offsets while providing the session start time updates the label of the timestamps
subset_series_helper.plot_pandas(use_absolute_times=False,
                                 session_start_time=infile.session_start_time,
                                 figsize=(12,5))
plt.show()

# Plotting with absolute times converts the time offsets to real times
subset_series_helper.plot_pandas(use_absolute_times=True,
                                 session_start_time=infile.session_start_time,
                                 figsize=(12,5))
plt.show()

####################
# Convert the TimeSeries to XArray
# -----------------------------------------------------------
#

xr = subset_series_helper.to_xarray(use_absolute_times=True,
                                    session_start_time=infile.session_start_time)
print(xr)

####################
# ``[Out]:``
#
#  .. code-block:: python
#
#        <xarray.DataArray (Time: 18, 0: 3)>
#        array([[0.868632, 0.876307, 0.883766],
#               [0.911403, 0.917755, 0.92388 ],
#               [0.946085, 0.951057, 0.955793],
#               [0.97237 , 0.975917, 0.979223],
#               [0.990024, 0.992115, 0.993961],
#               [0.99889 , 0.999507, 0.999877],
#               [0.99889 , 0.998027, 0.996917],
#               [0.990024, 0.987688, 0.985109],
#               [0.97237 , 0.968583, 0.964557],
#               [0.946085, 0.940881, 0.935444],
#               [0.911403, 0.904827, 0.898028],
#               [0.868632, 0.860742, 0.85264 ],
#               [0.81815 , 0.809017, 0.799685],
#               [0.760406, 0.750111, 0.739631],
#               [0.695913, 0.684547, 0.673013],
#               [0.625243, 0.612907, 0.60042 ],
#               [0.549023, 0.535827, 0.522499],
#               [0.46793 , 0.45399 , 0.439939]])
#        Coordinates:
#          * Time     (Time) datetime64[ns] 2018-06-12T18:08:25 ...
#        Dimensions without coordinates: 0
#        Attributes:
#            num_samples:         18
#            rate_unit:           Seconds
#            rate:                0.5
#            resolution:          0.0
#            description:         no description
#            starting_time:       72.0
#            unit:                SiUnit
#            comments:            no comments
#            conversion:          1.0
#            source:              PyNWB tutorial
#            session_start_time:  2018-06-12 18:07:13
#

####################
# Selecting data by time in the XArray
#

sel = xr.sel(Time='2018-06-12T18:08:25')
print(sel)

####################
# ``[Out]:``
#
#  .. code-block:: python
#
#        <xarray.DataArray (Time: 2, 0: 3)>
#        array([[0.868632, 0.876307, 0.883766],
#               [0.911403, 0.917755, 0.92388 ]])
#        Coordinates:
#          * Time     (Time) datetime64[ns] 2018-06-12T18:08:25 ...
#        Dimensions without coordinates: 0
#        Attributes:
#            num_samples:         18
#            rate_unit:           Seconds
#            rate:                0.5
#            resolution:          0.0
#            description:         no description
#            starting_time:       72.0
#            unit:                SiUnit
#            comments:            no comments
#            conversion:          1.0
#            source:              PyNWB tutorial
#            session_start_time:  2018-06-12 18:07:13
#

