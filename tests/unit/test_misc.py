import unittest

from pynwb import TimeSeries
from pynwb.misc import AnnotationSeries, AbstractFeatureSeries, IntervalSeries, SpikeUnit, UnitTimes

import numpy as np


class AnnotationSeriesConstructor(unittest.TestCase):
    def test_init(self):
        aS = AnnotationSeries('test_aS', 'a hypothetical source', timestamps=list())
        self.assertEqual(aS.name, 'test_aS')
        self.assertEqual(aS.source, 'a hypothetical source')

        aS.add_annotation(2.0, 'comment')

class AbstractFeatureSeriesConstructor(unittest.TestCase):
    def test_init(self):
        aFS = AbstractFeatureSeries('test_aFS', 'a hypothetical source', 'feature units', 'features', timestamps=list())
        self.assertEqual(aFS.name, 'test_aFS')
        self.assertEqual(aFS.source, 'a hypothetical source')
        self.assertEqual(aFS.feature_units, 'feature units')
        self.assertEqual(aFS.features, 'features')

        aFS.add_features(2.0, list())

class IntervalSeriesConstructor(unittest.TestCase):
    def test_init(self):
        data = [0, 1, 0, 1]
        iS = IntervalSeries('test_iS', 'a hypothetical source', data, timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.source, 'a hypothetical source')
        self.assertEqual(iS.data, data)

        iS.add_interval(1.0, 2.0)

class UnitTimesConstructor(unittest.TestCase):
    def test_init(self):
        unit_times = [1.0, 2.0]

        su1 = SpikeUnit(unit_times, 'unit_description_1', 'unit_source_1')
        self.assertEqual(su1.times, unit_times)
        self.assertEqual(su1.unit_description, 'unit_description_1')
        self.assertEqual(su1.source, 'unit_source_1')

        su2 = SpikeUnit(unit_times, 'unit_description_2', 'unit_source_2')
        self.assertEqual(su2.times, unit_times)
        self.assertEqual(su2.unit_description, 'unit_description_2')
        self.assertEqual(su2.source, 'unit_source_2')

        sul = [su1, su2]
        ut = UnitTimes('test_ut', sul)
        self.assertEqual(ut.source, 'test_ut')
        self.assertEqual(ut.spike_unit, sul)

if __name__ == '__main__':
    unittest.main()

