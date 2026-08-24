"""Test that pynwb accepts zarr arrays in array-valued fields and when determining lengths.

A zarr v3 ``Array`` exposes ``shape`` and ``__getitem__`` but implements neither ``__iter__`` nor
``__len__``. zarr is not a pynwb dependency, so these tests are skipped when zarr v3 is not installed.

See https://github.com/NeurodataWithoutBorders/pynwb/issues/2234.
"""
import unittest
import warnings

import numpy as np
from hdmf.common import DynamicTableRegion

from pynwb import TimeSeries
from pynwb.ecephys import ElectricalSeries
from pynwb.image import ImageSeries
from pynwb.ophys import TwoPhotonSeries
from pynwb.testing import TestCase
from pynwb.testing.mock.ecephys import mock_ElectrodesTable
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.testing.mock.ophys import mock_ImagingPlane

try:
    import zarr
    ZARR_V3_AVAILABLE = int(zarr.__version__.split('.')[0]) >= 3
except ImportError:
    ZARR_V3_AVAILABLE = False


def zarr_array(data):
    """Return a zarr array holding ``data``."""
    array = np.asarray(data)
    with warnings.catch_warnings():
        # zarr v3 flags fixed-length string dtypes as having no stable specification
        warnings.simplefilter("ignore")
        ret = zarr.create_array(store={}, shape=array.shape, dtype=array.dtype)
        ret[...] = array
    return ret


@unittest.skipUnless(ZARR_V3_AVAILABLE, "zarr v3 is not installed")
class TestZarrArrayFields(TestCase):
    """Construct containers whose array-valued fields are backed by zarr arrays."""

    def test_time_series_control(self):
        ts = TimeSeries(
            name="ts",
            data=np.arange(3.0),
            unit="volts",
            timestamps=np.arange(3.0),
            control=zarr_array([0, 1, 2]),
            control_description=zarr_array(["a", "b", "c"]),
        )
        np.testing.assert_array_equal(ts.control[:], [0, 1, 2])
        np.testing.assert_array_equal(ts.control_description[:], ["a", "b", "c"])

    def test_image_series_dimension_and_starting_frame(self):
        image_series = ImageSeries(
            name="is",
            unit="n/a",
            format="external",
            external_file=["a.mp4", "b.mp4"],
            starting_frame=zarr_array([0, 10]),
            dimension=zarr_array([32, 32]),
            num_samples=20,
            rate=1.0,
        )
        np.testing.assert_array_equal(image_series.starting_frame[:], [0, 10])
        np.testing.assert_array_equal(image_series.dimension[:], [32, 32])

    def test_two_photon_series_field_of_view(self):
        two_photon_series = TwoPhotonSeries(
            name="tps",
            imaging_plane=mock_ImagingPlane(),
            data=np.zeros((3, 2, 2)),
            unit="n/a",
            rate=1.0,
            field_of_view=zarr_array([1.0, 2.0]),
        )
        np.testing.assert_array_equal(two_photon_series.field_of_view[:], [1.0, 2.0])

    def _electrodes_region(self, n_electrodes):
        nwbfile = mock_NWBFile()
        table = mock_ElectrodesTable(n_rows=n_electrodes, nwbfile=nwbfile)
        return DynamicTableRegion(
            name="electrodes",
            data=zarr_array(list(range(n_electrodes))),
            description="the electrodes",
            table=table,
        )

    def test_electrical_series_electrodes(self):
        electrodes = self._electrodes_region(3)
        electrical_series = ElectricalSeries(
            name="es", data=np.zeros((5, 3)), electrodes=electrodes, rate=1.0
        )
        np.testing.assert_array_equal(electrical_series.electrodes.data[:], [0, 1, 2])

    def test_electrical_series_electrodes_transposed(self):
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
