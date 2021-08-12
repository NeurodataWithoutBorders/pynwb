from pynwb import NWBHDF5IO
from pynwb.testing import TestCase


class TestRos3Streaming(TestCase):
    # requires h5py to be built with the ROS3 driver: conda install -c conda-forge h5py
    # also requires requests package to be installed

    def test_read(self):
        s3_path = 'https://dandiarchive.s3.amazonaws.com/ros3test.nwb'

        with NWBHDF5IO(s3_path, mode='r', load_namespaces=True, driver='ros3') as io:
            nwbfile = io.read()
            test_data = nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:]
            self.assertEqual(len(test_data), 1046)
