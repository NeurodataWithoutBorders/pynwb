"""Guard the docval types of array-valued fields that accept array-API arrays.

zarr v3 ``Array`` exposes ``shape`` and ``__getitem__`` but implements neither
``__iter__`` nor ``__len__``, so it does not satisfy
``isinstance(x, collections.abc.Iterable)``. Fields that hold array data therefore
use the ``('array_data', 'data')`` docval type, whose ``array_data`` macro includes
``zarr.Array``. That type accepts array-like values and rejects non-array iterables
such as ``set``. ``NWBFile.electrode_groups`` holds ``ElectrodeGroup`` objects and is
never backed by a dataset, so it uses ``Iterable`` and accepts any iterable.

See https://github.com/NeurodataWithoutBorders/pynwb/issues/2234.
"""
import numpy as np
from hdmf.utils import check_type, get_docval

from pynwb.base import TimeSeries
from pynwb.image import ImageSeries, OpticalSeries
from pynwb.misc import AbstractFeatureSeries
from pynwb.ecephys import Clustering, ClusterWaveforms
from pynwb.file import NWBFile
from pynwb.ophys import TwoPhotonSeries
from pynwb.testing import TestCase


def _field_type(func, name):
    (spec,) = [d for d in get_docval(func) if d['name'] == name]
    return spec['type']


class TestArrayDataFieldTypes(TestCase):

    def test_array_valued_fields_accept_array_data_reject_non_array_iterable(self):
        cases = [
            (TimeSeries.__init__, 'control'),
            (TimeSeries.__init__, 'control_description'),
            (ImageSeries.__init__, 'dimension'),
            (ImageSeries.__init__, 'starting_frame'),
            (AbstractFeatureSeries.__init__, 'features'),
            (AbstractFeatureSeries.__init__, 'feature_units'),
            (Clustering.__init__, 'peak_over_rms'),
            (ClusterWaveforms.__init__, 'waveform_mean'),
            (ClusterWaveforms.__init__, 'waveform_sd'),
            (OpticalSeries.__init__, 'field_of_view'),
            (TwoPhotonSeries.__init__, 'field_of_view'),
        ]
        for func, name in cases:
            with self.subTest(field=name):
                field_type = _field_type(func, name)
                self.assertTrue(check_type(np.array([0, 1, 2]), field_type))
                self.assertTrue(check_type([0, 1, 2], field_type))
                self.assertFalse(check_type({0, 1, 2}, field_type))

    def test_electrode_groups_holds_objects_accepts_any_iterable(self):
        field_type = _field_type(NWBFile.__init__, 'electrode_groups')
        self.assertTrue(check_type({0, 1, 2}, field_type))
