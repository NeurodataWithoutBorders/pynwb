import os
from pynwb.base import TimeSeriesReference
from pynwb import NWBHDF5IO
from pynwb.testing import TestCase
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.testing.mock.base import mock_TimeSeries
from pynwb.misc import Units


class TestFileCopy(TestCase):

    def setUp(self):
        self.path1 = "test_a.nwb"
        self.path2 = "test_b.nwb"

    def tearDown(self):
        if os.path.exists(self.path1):
            os.remove(self.path1)
        if os.path.exists(self.path2):
            os.remove(self.path2)

    def test_copy_file_link_timeintervals_timeseries(self):
        """Test copying a file with a TimeSeriesReference in a TimeIntervals object and reading that copy.

        Based on https://github.com/NeurodataWithoutBorders/pynwb/issues/1863
        """
        new_nwb = mock_NWBFile()
        test_ts = mock_TimeSeries(name="test_ts", timestamps=[1.0, 2.0, 3.0], data=[1.0, 2.0, 3.0])
        new_nwb.add_acquisition(test_ts)
        new_nwb.add_trial(start_time=1.0, stop_time=2.0, timeseries=[test_ts])

        with NWBHDF5IO(self.path1, 'w') as io:
            io.write(new_nwb)

        with NWBHDF5IO(self.path1, 'r') as base_io:
            # the TimeIntervals object is copied but the TimeSeriesReferenceVectorData is linked
            nwb_add = base_io.read().copy()
            with NWBHDF5IO(self.path2, 'w', manager=base_io.manager) as out_io:
                out_io.write(nwb_add)

        with NWBHDF5IO(self.path2, 'r') as io:
            nwb = io.read()
            ts_val = nwb.trials["timeseries"][0][0]
            assert isinstance(ts_val, TimeSeriesReference)
            assert ts_val.timeseries is nwb.acquisition["test_ts"]

    def test_copy_file_link_units_columns(self):
        """Test copying a file with a Units table whose columns are linked and reading that copy.

        Based on https://github.com/NeurodataWithoutBorders/pynwb/issues/1223
        """
        new_nwb = mock_NWBFile()
        new_nwb.units = Units(
            name="units",
            description="units table",
            resolution=0.001,
            waveform_rate=30000.0,
            waveform_unit="microvolts",
        )
        new_nwb.add_unit(spike_times=[1.0, 2.0, 3.0], waveform_mean=[1.0, 2.0, 3.0])

        with NWBHDF5IO(self.path1, 'w') as io:
            io.write(new_nwb)

        with NWBHDF5IO(self.path1, 'r') as base_io:
            # the Units object is copied but its columns are linked
            nwb_add = base_io.read().copy()
            with NWBHDF5IO(self.path2, 'w', manager=base_io.manager) as out_io:
                out_io.write(nwb_add)

        with NWBHDF5IO(self.path2, 'r') as io:
            nwb = io.read()
            self.assertEqual(nwb.units.resolution, 0.001)
            self.assertEqual(nwb.units.waveform_rate, 30000.0)
            self.assertEqual(nwb.units.waveform_unit, "microvolts")
            self.assertListEqual(list(nwb.units["spike_times"][0]), [1.0, 2.0, 3.0])
