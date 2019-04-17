import unittest2 as unittest

from datetime import datetime
from dateutil.tz import tzlocal
from pynwb import NWBFile




class TestVectorData(unittest.TestCase):
    def setUp(self):
        self.nwbfile = NWBFile("a file with header data", "NB123A", datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzlocal()))

    def test_empty_data(self):
        data = []
        index = [0,0,0]
        self.nwbfile.add_trial(start_time=.1, stop_time=.2)
        self.nwbfile.add_trial(start_time=.3, stop_time=.4)
        self.nwbfile.add_trial(start_time=.5, stop_time=.6)
        self.nwbfile.add_trial_column(name='example', description='Hi', data=data, index=index)
        self.assertListEqual(self.nwbfile.trials['example'][0], [])
        self.assertListEqual(self.nwbfile.trials['example'][1], [])
        self.assertListEqual(self.nwbfile.trials['example'][2], [])

    def test_empty_data_nonempty_index(self):
        data = []
        index = [1,0,0]
        self.nwbfile.add_trial(start_time=.1, stop_time=.2)
        self.nwbfile.add_trial(start_time=.3, stop_time=.4)
        self.nwbfile.add_trial(start_time=.5, stop_time=.6)
        with self.assertRaisesRegex(ValueError, "cannot pass non-empty index with empty data to index"):
            self.nwbfile.add_trial_column(name='example', description='Hi', data=data, index=index)
