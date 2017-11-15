
def main():

    # prerequisites: start
    import numpy as np

    electrode_name = 'tetrode1'
    rate = 10.0
    np.random.seed(1234)
    data_len = 1000
    ephys_data = np.random.rand(data_len)
    ephys_timestamps = np.arange(data_len) / rate
    spatial_timestamps = ephys_timestamps[::10]
    spatial_data = np.cumsum(np.random.normal(size=(2, len(spatial_timestamps))), axis=-1).T
    # prerequisites: end

    # create-nwbfile: start
    from datetime import datetime
    from pynwb import NWBFile

    f = NWBFile('the PyNWB tutorial', 'my first synthetic recording', 'EXAMPLE_ID', datetime.now(),
                experimenter='Dr. Bilbo Baggins',
                lab='Bag End Laboratory',
                institution='University of Middle Earth at the Shire',
                experiment_description='I went on an adventure with thirteen dwarves to reclaim vast treasures.',
                session_id='LONELYMTN')
    # create-nwbfile: end

    # save-nwbfile: start
    from pynwb.form.backends.hdf5 import HDF5IO

    filename = "example.h5"
    io = HDF5IO(filename, mode='w')
    io.write(f)
    io.close()
    # save-nwbfile: end

    # create-epochs: start
    epoch_tags = ('example_epoch',)

    ep1 = f.create_epoch('epoch1', ephys_timestamps[100], ephys_timestamps[200],
                         tags=epoch_tags,
                         description="the first test epoch")

    ep2 = f.create_epoch('epoch2', ephys_timestamps[600], ephys_timestamps[700],
                         tags=epoch_tags,
                         description="the second test epoch")
    # create-epochs: end


    # create-device: start
    device = f.create_device('trodes_rig123')
    # create-device: end

    # create-electrode-groups: start
    channel_description = ['channel1', 'channel2', 'channel3', 'channel4']
    num_channels = len(channel_description)
    channel_location = ['CA1'] * num_channels
    channel_filtering = ['no filtering'] * num_channels
    channel_coordinates = [(2.0, 2.0, 2.0)] * num_channels
    channel_impedance = [-1] * num_channels
    description = "an example tetrode"
    location = "somewhere in the hippocampus"

    electrode_group = f.create_electrode_group(electrode_name,
                                               channel_description,
                                               channel_location,
                                               channel_filtering,
                                               channel_coordinates,
                                               channel_impedance,
                                               description,
                                               location,
                                               device)
    # create-electrode-groups: end

    # create-timeseries: start
    from pynwb.ecephys import ElectricalSeries
    from pynwb.behavior import SpatialSeries

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
                                description="Random numbers generated with numpy.random.rand")
    f.add_raw_timeseries(ephys_ts, [ep1, ep2])

    spatial_ts = SpatialSeries('test_spatial_timeseries',
                               'a stumbling rat',
                               spatial_data,
                               'origin on x,y-plane',
                               timestamps=spatial_timestamps,
                               resolution=0.1,
                               comments="This data was generated with numpy, using 1234 as the seed",
                               description="This 2D Brownian process generated with "
                                           "np.cumsum(np.random.normal(size=(2, len(spatial_timestamps))), axis=-1).T")
    f.add_raw_timeseries(spatial_ts, [ep1, ep2])
    # create-timeseries: end

if __name__ == "__main__":
    main()
