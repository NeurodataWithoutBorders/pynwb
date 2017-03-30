import unittest

from pynwb import TimeSeries
from pynwb.misc import AnnotationSeries, AbstractFeatureSeries, IntervalSeries, UnitTimes

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
        iS = IntervalSeries('test_iS', 'a hypothetical source')
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.source, 'a hypothetical source')

        iS.add_interval(1.0, 2.0)

class UnitTimesConstructor(unittest.TestCase):
    def test_init(self):
        unit_times = [1.0, 2.0]
        ut = UnitTimes('test_ut', unit_times, 'unit_description', 'unit_source')
        self.assertEqual(ut.source, 'test_ut')
        self.assertEqual(ut.unit_times, unit_times)
        self.assertEqual(ut.unit_description, 'unit_description')
        self.assertEqual(ut.unit_source, 'unit_source')


if __name__ == '__main__':
    unittest.main()
