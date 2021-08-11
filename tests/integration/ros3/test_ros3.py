from pynwb import NWBHDF5IO
from pynwb.testing import TestCase
from pynwb.utils import get_dandi_s3_url


class TestRos3Streaming(TestCase):
    # requires h5py to be built with the ROS3 driver: conda install -c conda-forge h5py
    # also requires requests package to be installed

    def test_read(self):
        # ephys, Svoboda Lab (450 kB)
        dandiset_id = '000006'
        filepath = 'sub-anm372795/sub-anm372795_ses-20170718.nwb'
        s3_path = get_dandi_s3_url(dandiset_id, filepath)

        with NWBHDF5IO(s3_path, mode='r', load_namespaces=True, driver='ros3') as io:
            nwbfile = io.read()
            test_data = nwbfile.acquisition['lick_times'].time_series['lick_left_times'].data[:]
            self.assertEqual(len(test_data), 1046)
