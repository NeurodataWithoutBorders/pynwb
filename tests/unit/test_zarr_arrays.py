"""Test that pynwb determines the length of zarr-backed data without calling ``len()`` on it.

A zarr v3 ``Array`` exposes ``shape`` and ``__getitem__`` but implements neither ``__iter__`` nor
``__len__``. zarr is not a pynwb dependency, so these tests are skipped when zarr v3 is not installed.

See https://github.com/NeurodataWithoutBorders/pynwb/issues/2234.
"""
import unittest

import numpy as np
from hdmf.common import DynamicTableRegion

from pynwb import TimeSeries
from pynwb.ecephys import ElectricalSeries
from pynwb.testing import TestCase
from pynwb.testing.mock.ecephys import mock_ElectrodesTable
from pynwb.testing.mock.file import mock_NWBFile

try:
    import zarr
    ZARR_V3_AVAILABLE = int(zarr.__version__.split('.')[0]) >= 3
except ImportError:
    ZARR_V3_AVAILABLE = False


def zarr_array(data):
    """Return a zarr array holding ``data``."""
    array = np.asarray(data)
    ret = zarr.create_array(store={}, shape=array.shape, dtype=array.dtype)
    ret[...] = array
    return ret


@unittest.skipUnless(ZARR_V3_AVAILABLE, "zarr v3 is not installed")
class TestZarrArrayElectrodes(TestCase):
    """Count the electrodes of an ElectricalSeries whose electrodes region is backed by a zarr array."""

    def _electrodes_region(self, n_electrodes):
        nwbfile = mock_NWBFile()
        table = mock_ElectrodesTable(n_rows=n_electrodes, nwbfile=nwbfile)
        return DynamicTableRegion(
            name="electrodes",
            data=zarr_array(list(range(n_electrodes))),
            description="the electrodes",
            table=table,
        )

    def test_electrodes_match_second_dimension(self):
        electrodes = self._electrodes_region(3)
        electrical_series = ElectricalSeries(
            name="es", data=np.zeros((5, 3)), electrodes=electrodes, rate=1.0
        )
        np.testing.assert_array_equal(electrical_series.electrodes.data[:], [0, 1, 2])

    def test_electrodes_match_first_dimension(self):
        electrodes = self._electrodes_region(3)
        msg = (
            "ElectricalSeries 'es': The second dimension of data does not match the length of electrodes, "
            "but instead the first does. Data is oriented incorrectly and should be transposed."
        )
        with self.assertWarnsWith(UserWarning, msg):
            ElectricalSeries(name="es", data=np.zeros((3, 5)), electrodes=electrodes, rate=1.0)


@unittest.skipUnless(ZARR_V3_AVAILABLE, "zarr v3 is not installed")
class TestZarrArrayNumSamples(TestCase):
    """Determine the number of samples of a TimeSeries whose data is backed by a zarr array."""

    def setUp(self):
        self.ts = TimeSeries(name="ts", data=zarr_array(np.arange(5.0)), unit="volts", rate=10.0)

    def test_num_samples(self):
        self.assertEqual(self.ts.num_samples, 5)

    def test_get_timestamps(self):
        np.testing.assert_allclose(self.ts.get_timestamps(), np.arange(5) / 10.0)
