
def main():

    import os.path

    # prerequisites: start
    import numpy as np

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
    from pynwb import get_manager
    from pynwb.form.backends.hdf5 import HDF5IO

    filename = "example.h5"
    io = HDF5IO(filename, manager=get_manager(), mode='w')
    io.write(f)
    io.close()
    # save-nwbfile: end

    os.remove(filename)

    # create-epochs: start
    epoch_tags = ('example_epoch',)

    ep1 = f.create_epoch(source='an hypothetical source', name='epoch1', start=0.0, stop=1.0,
                         tags=epoch_tags,
                         description="the first test epoch")

    ep2 = f.create_epoch(source='an hypothetical source', name='epoch2', start=0.0, stop=1.0,
                         tags=epoch_tags,
                         description="the second test epoch")
    # create-epochs: end

    # create-device: start
    device = f.create_device(name='trodes_rig123', source="a source")
    # create-device: end

    # create-electrode-groups: start
    electrode_name = 'tetrode1'
    source = "an hypothetical source"
    description = "an example tetrode"
    location = "somewhere in the hippocampus"

    electrode_group = f.create_electrode_group(electrode_name,
                                               source=source,
                                               description=description,
                                               location=location,
                                               device=device)

    # create-electrode-groups: end

    # create-electrode-table-region: start
    for idx in [1, 2, 3, 4]:
        f.add_electrode(idx,
                        x=1.0, y=2.0, z=3.0,
                        imp=float(-idx),
                        location='CA1', filtering='none',
                        description='channel %s' % idx, group=electrode_group)

    electrode_table_region = f.create_electrode_table_region([0, 2], 'the first and third electrodes')
    # create-electrode-table-region: end

    # create-timeseries: start
    from pynwb.ecephys import ElectricalSeries
    from pynwb.behavior import SpatialSeries

    ephys_ts = ElectricalSeries('test_ephys_data',
                                'an hypothetical source',
                                ephys_data,
                                electrode_table_region,
                                timestamps=ephys_timestamps,
                                # Alternatively, could specify starting_time and rate as follows
                                # starting_time=ephys_timestamps[0],
                                # rate=rate,
                                resolution=0.001,
                                comments="This data was randomly generated with numpy, using 1234 as the seed",
                                description="Random numbers generated with numpy.random.rand")
    f.add_acquisition(ephys_ts, [ep1, ep2])

    spatial_ts = SpatialSeries('test_spatial_timeseries',
                               'a stumbling rat',
                               spatial_data,
                               'origin on x,y-plane',
                               timestamps=spatial_timestamps,
                               resolution=0.1,
                               comments="This data was generated with numpy, using 1234 as the seed",
                               description="This 2D Brownian process generated with "
                                           "np.cumsum(np.random.normal(size=(2, len(spatial_timestamps))), axis=-1).T")
    f.add_acquisition(spatial_ts, [ep1, ep2])
    # create-timeseries: end

    # create-data-interface: start
    from pynwb.ecephys import LFP
    from pynwb.behavior import Position

    lfp = f.add_acquisition(LFP('a hypothetical source'))
    ephys_ts = lfp.create_electrical_series('test_ephys_data',
                                            'an hypothetical source',
                                            ephys_data,
                                            electrode_table_region,
                                            timestamps=ephys_timestamps,
                                            resolution=0.001,
                                            comments="This data was randomly generated with numpy, using 1234 as the seed",  # noqa: E501
                                            description="Random numbers generated with numpy.random.rand")
    f.set_epoch_timeseries([ep1, ep2], ephys_ts)

    pos = f.add_acquisition(Position('a hypothetical source'))
    spatial_ts = pos.create_spatial_series('test_spatial_timeseries',
                                           'a stumbling rat',
                                           spatial_data,
                                           'origin on x,y-plane',
                                           timestamps=spatial_timestamps,
                                           resolution=0.1,
                                           comments="This data was generated with numpy, using 1234 as the seed",
                                           description="This 2D Brownian process generated with "
                                                       "np.cumsum(np.random.normal(size=(2, len(spatial_timestamps))), axis=-1).T")  # noqa: E501
    f.set_epoch_timeseries([ep1, ep2], spatial_ts)
    # create-data-interface: end

    # create-compressed-timeseries: start
    from pynwb.ecephys import ElectricalSeries
    from pynwb.behavior import SpatialSeries
    from pynwb.form.backends.hdf5 import H5DataIO

    ephys_ts = ElectricalSeries('test_compressed_ephys_data',
                                'an hypothetical source',
                                H5DataIO(ephys_data, compress=True),
                                electrode_table_region,
                                timestamps=H5DataIO(ephys_timestamps, compress=True),
                                resolution=0.001,
                                comments="This data was randomly generated with numpy, using 1234 as the seed",
                                description="Random numbers generated with numpy.random.rand")
    f.add_acquisition(ephys_ts, [ep1, ep2])

    spatial_ts = SpatialSeries('test_compressed_spatial_timeseries',
                               'a stumbling rat',
                               H5DataIO(spatial_data, compress=True),
                               'origin on x,y-plane',
                               timestamps=H5DataIO(spatial_timestamps, compress=True),
                               resolution=0.1,
                               comments="This data was generated with numpy, using 1234 as the seed",
                               description="This 2D Brownian process generated with "
                                           "np.cumsum(np.random.normal(size=(2, len(spatial_timestamps))), axis=-1).T")
    f.add_acquisition(spatial_ts, [ep1, ep2])
    # create-compressed-timeseries: end

if __name__ == "__main__":
    main()
