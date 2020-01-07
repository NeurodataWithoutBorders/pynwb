from pynwb.ecephys import ElectricalSeries
from pynwb.behavior import SpatialSeries
from pynwb import NWBFile, get_build_manager
from form.backends.hdf5 import HDF5IO

import numpy as np
import os
from datetime import datetime
from dateutil.tz import tzlocal

data_len = 1000
filename = 'test.nwb'


if os.path.exists(filename):
    print('removing %s' % filename)
    os.remove(filename)

f = NWBFile(filename, 'my first synthetic recording', 'EXAMPLE_ID', datetime.now(tzlocal()),
            experimenter='Dr. Bilbo Baggins',
            lab='Bag End Labatory',
            institution='University of Middle Earth at the Shire',
            experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
            stimulus_notes='The one ring to rule them all has been found',
            data_collection='The ring was found in cave and stolen from Gollum',
            session_id='LONELYMTN')

# Create the electrode group this simulated data is generated from
electrode_name = 'tetrode1'
channel_description = ['channel1', 'channel2', 'channel3', 'channel4']
num_channels = len(channel_description)
channel_location = ['CA1'] * num_channels
channel_filtering = ['no filtering'] * num_channels
channel_coordinates = [(2.0, 2.0, 2.0)] * num_channels
channel_impedance = [-1] * num_channels
description = "an example tetrode"
location = "somewhere in the hippocampus"
device = f.create_device('trodes_rig123')


electrode_group = f.create_electrode_group(electrode_name,
                                           channel_description,
                                           channel_location,
                                           channel_filtering,
                                           channel_coordinates,
                                           channel_impedance,
                                           description,
                                           location,
                                           device)

# Create the TimeSeries object for the eletrophysiology data

# Make some fake data
rate = 10.0
np.random.seed(1234)
ephys_data = np.random.rand(data_len)
ephys_timestamps = np.arange(data_len) / rate
spatial_timestamps = ephys_timestamps[::10]
spatial_data = np.cumsum(np.random.normal(size=(2, len(spatial_timestamps))), axis=-1).T

ephys_ts = ElectricalSeries('test_ephys_data',
                            'test_source',
                            ephys_data,
                            electrode_group,
                            timestamps=ephys_timestamps,
                            # Alternatively, could specify starting_time and rate as follows
                            # starting_time=ephys_timestamps[0],
                            # rate=rate,
                            resolution=0.001,
                            comments="This data was randomly generated with numpy, using 1234 as the seed",
                            description="Random numbers generated with numpy.randon.rand")

spatial_ts = SpatialSeries('test_spatial_data',
                           'a stumbling rat',
                           spatial_data,
                           'origin on x,y-plane',
                           timestamps=spatial_timestamps,
                           resolution=0.1,
                           comments="This data was generated with numpy, using 1234 as the seed",
                           description="This 2D Brownian process generated with \
                           numpy.cumsum(numpy.random.normal(size=(2,len(spatial_timestamps))), axis=-1).T")

# Create experimental epochs
epoch_tags = ('test_example',)
ep1 = f.add_epoch('epoch1', ephys_timestamps[100], ephys_timestamps[200],
                  tags=epoch_tags, description="the first test epoch")
ep2 = f.add_epoch('epoch2', ephys_timestamps[600], ephys_timestamps[700],
                  tags=epoch_tags, description="the second test epoch")

# Add the time series data and include the epochs it is apart of
f.add_raw_timeseries(ephys_ts, [ep1, ep2])
f.add_raw_timeseries(spatial_ts, [ep1, ep2])

# Write the NWB file
manager = get_build_manager()

io = HDF5IO(filename, manager, mode='w')
io.write(f)
io.close()
io = HDF5IO(filename, manager, mode='r')
io.read()
io.close()
