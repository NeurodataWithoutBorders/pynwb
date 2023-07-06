from pynwb.testing.mock.ecephys import (
    mock_ElectrodeGroup,
    mock_ElectrodeTable,
    mock_ElectricalSeries,
    mock_SpikeEventSeries,
    mock_electrodes
)
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.testing import TestCase

class TestMockElectricalSeries(TestCase):

    def set_up_dependencies(self):
        nwbfile = mock_NWBFile()
        return nwbfile

    def test_mock_electrode_group_nwbfile(self):
        pass

    def test_mock_electrode_group_nwbfile_none(self):
        pass

    def test_mock_electrode_group_device_nwbfile(self):
        pass

    def test_mock_electrode_group_device_nwbfile_error(self):
        pass

    def test_mock_electrode_table_nwbfile(self):
        pass

    def test_mock_electrode_table_group(self):
        pass

    def test_mock_electrode_table_group_nwbfile(self):
        pass

    def test_mock_electrode_table_group_nwbfile_error(self):
        pass

    def test_mock_electrodes_nwbfile(self):
        pass

    def test_mock_electrodes_table_nwbfile(self):
        pass

    def test_mock_electrical_series_nwbfile(self):
        nwbfile = self.set_up_dependencies()
        series = mock_ElectricalSeries(nwbfile=nwbfile)
        self.assertEqual(type(series.electrodes.table.parent).__name__, 'NWBFile')
        self.assertEqual(type(series.parent).__name__, 'NWBFile')

    def test_mock_electrical_series_nwbfile_error(self):
        pass

    def test_mock_electrical_series_electrodes_nwbfile(self):
        pass
