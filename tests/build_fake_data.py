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

f = NWBFile(filename, 'my first synthetic recording',
            experimenter='Dr. Bilbo Baggins',
            lab='Bag End Labatory',
            institution='University of Middle Earth at the Shire',
            experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
            session_id='LONELYMTN')

# Create the electrode group this simulated data is generated from
electrode_name = 'electrode1'
f.create_electrode_group(electrode_name, (2.0,2.0,2.0), 'a lonely probe', 'trodes_rig123', 'the most desolate or brain regions')

# Create the TimeSeries object for the eletrophysiology data
description = "This is a test TimeSeries dataset, and has no scientific value"
comments = "After a long journey there and back again, the treasures have been returned to their rightful owners."

rate = 10.0
np.random.seed(1)
data = np.random.rand(data_len)
timestamps = np.arange(data_len) / rate

ts = ElectricalSeries('test_timeseries',
                      [electrode_name],
                      'test_source',
                      data=data,  
                      timestamps=timestamps,
                      # Alternatively, could specify starting_time and rate as follows
                      #starting_time=timestamps[0],
                      #rate=rate,
                      resolution=0.01,
                      comments=comments,
                      description=description)

# Create experimental epochs
epoch_tags = ('test_example',)
ep1 = f.create_epoch('epoch1', timestamps[100], timestamps[200], tags=epoch_tags, description="the first test epoch")
ep2 = f.create_epoch('epoch2', timestamps[600], timestamps[700], tags=epoch_tags, description="the second test epoch")

# Add the time series data and include the epochs it is apart of
f.add_raw_data(ts, [ep1, ep2])

# Write the NWB file
writer = HDF5Writer()
writer.write(f, f.filename)
