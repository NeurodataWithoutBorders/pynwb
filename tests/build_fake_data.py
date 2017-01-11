from pynwb.ui.file import NWBFile
from pynwb.ui.timeseries import ElectricalSeries, SpatialSeries
from pynwb.io.write import HDF5Writer
#from pynwb.ui.epoch import Epoch
#from pynwb.ui.ephys import ElectrodeGroup

import numpy as np
import scipy.stats as sps
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
electrode_name = 'tetrode1'
f.create_electrode_group(electrode_name, (2.0,2.0,2.0), 'a lonely probe', 'trodes_rig123', 'the most desolate or brain regions')

# Create the TimeSeries object for the eletrophysiology data

# Make some fake data
rate = 10.0
np.random.seed(1234)
ephys_data = np.random.rand(data_len)
ephys_timestamps = np.arange(data_len) / rate
spatial_timestamps = ephys_timestamps[::10]
spatial_data = np.cumsum(sps.norm.rvs(size=(2,len(spatial_timestamps))), axis=-1).T 

ephys_ts = ElectricalSeries('test_timeseries',
                            'test_source',
                            ephys_data,
                            [electrode_name],
                            timestamps=ephys_timestamps,
                            # Alternatively, could specify starting_time and rate as follows
                            #starting_time=ephys_timestamps[0],
                            #rate=rate,
                            resolution=0.001,
                            comments="This data was randomly generated with numpy, using 1234 as the seed",
                            description="Random numbers generated with numpy.randon.rand")

spatial_ts = SpatialSeries('test_spatial_timeseries',
                           'a stumbling rat',
                           spatial_data,
                           'origin on x,y-plane',
                           timestamps=spatial_timestamps,
                           resolution=0.1,
                           comments="This data was generated with numpy, using 1234 as the seed",
                           description="This 2D Brownian process generated with numpy.cumsum(scipy.stats.norm.rvs(size=(2,len(timestamps))), axis=-1).T")

# Create experimental epochs
epoch_tags = ('test_example',)
ep1 = f.create_epoch('epoch1', ephys_timestamps[100], ephys_timestamps[200], tags=epoch_tags, description="the first test epoch")
ep2 = f.create_epoch('epoch2', ephys_timestamps[600], ephys_timestamps[700], tags=epoch_tags, description="the second test epoch")

# Add the time series data and include the epochs it is apart of
f.add_raw_timeseries(ephys_ts, [ep1, ep2])
f.add_raw_timeseries(spatial_ts, [ep1, ep2])

# Write the NWB file
writer = HDF5Writer()
writer.write(f, f.filename)
