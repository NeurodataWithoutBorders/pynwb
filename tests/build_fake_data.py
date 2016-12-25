from pynwb.ui.file import NWBFile
from pynwb.ui.timeseries import ElectricalSeries
from pynwb.io.write import HDF5Writer
#from pynwb.ui.epoch import Epoch
#from pynwb.ui.ephys import ElectrodeGroup

import numpy as np
import os

data_len = 1000
filename = 'test.nwb'


if os.path.exists(filename):
    print('removing %s' % filename)
    os.remove(filename)

f = NWBFile(filename, 'my first synthetic recording')

rate = 10.0
data = np.fromiter(range(data_len), dtype=np.float)
timestamps = np.arange(data_len) / rate
description = "this is a test TimeSeries dataset, and has no scientific value"
comments = "After shaving yaks for 6 months, this dataset came to life"
unit="millivolts"



etrd_grp_idx = 1
ts = ElectricalSeries('test_timeseries',
                      [etrd_grp_idx],
                      'test_source',
                      data=data,  
                      timestamps=timestamps,
                      resolution=0.01,
                      unit=unit,
                      starting_time=timestamps[0],
                      rate=rate,
                      comments=comments,
                      description=description)

ep1 = f.create_epoch('epoch1', timestamps[100], timestamps[200], description="the first test epoch")
ep2 = f.create_epoch('epoch1', timestamps[600], timestamps[700], description="the second test epoch")

f.add_raw_data(ts, [ep1, ep2])

f.create_electrode_group(etrd_grp_idx, (2.0,2.0,2.0), 'a lonely probe', 'trodes_rig123', 'the most desolate or brain regions')

writer = HDF5Writer()
writer.write(f, f.filename)
