from datetime import datetime
from dateutil.tz import tzlocal

import numpy as np
from pynwb import NWBFile, TimeSeries

from .common import Benchmark

# Common useful pre-instantiated variables
# which do not need to be re-created and could be reused across benchmarks

start_time = datetime(2019, 4, 3, 11, tzinfo=tzlocal())
timestamps = np.linspace(0, 100, 1024)
timeseries_data = np.sin(0.333 * timestamps) + np.cos(0.1 * timestamps)


class Create(Benchmark):

    def time_NWBFile(self):
        NWBFile(session_description='benchmark',
                identifier='SOME',
                session_start_time=start_time)

    def time_TimeSeries(self):
        TimeSeries(
            name='raw_timeseries',
            data=timeseries_data,
            unit='m',
            timestamps=timestamps)
