import unittest

import numpy as np

from pynwb.misc import AnnotationSeries, AbstractFeatureSeries, IntervalSeries, UnitTimes


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
        data = [1.0, -1.0, 1.0, -1.0]
        timestamps = [0.0, 1.0, 2.0, 3.0]
        iS = IntervalSeries('test_iS', 'a hypothetical source', data=data, timestamps=timestamps)
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.source, 'a hypothetical source')
        self.assertEqual(iS.data, data)
        self.assertEqual(iS.timestamps, timestamps)

    def test_add_interval(self):
        data = [1.0, -1.0, 1.0, -1.0]
        timestamps = [0.0, 1.0, 2.0, 3.0]
        iS = IntervalSeries('test_iS', 'a hypothetical source', data=data, timestamps=timestamps)
        iS.add_interval(4.0, 5.0)
        data.append(1.0)
        data.append(-1.0)
        timestamps.append(4.0)
        timestamps.append(5.0)
        self.assertEqual(iS.data, data)
        self.assertEqual(iS.timestamps, timestamps)


class UnitTimesConstructor(unittest.TestCase):
    def test_init(self):
        ut = UnitTimes('UnitTimes constructor unit test')
        self.assertEqual(ut.source, 'UnitTimes constructor unit test')
        self.assertEqual(ut.name, 'UnitTimes')
        self.assertEqual(ut.unit_ids.data, list())
        self.assertEqual(ut.spike_times.data, list())
        self.assertEqual(ut.spike_times_index.data, list())

    def test_add_spike_times(self):
        ut = UnitTimes('UnitTimes add_spike_times unit test')
        ut.add_spike_times(0, [0, 1, 2])
        ut.add_spike_times(1, [3, 4, 5])
        self.assertEqual(ut.unit_ids.data, [0, 1])
        self.assertEqual(ut.spike_times.data, [0, 1, 2, 3, 4, 5])
        self.assertEqual(ut.spike_times_index.data, [3, 6])
        self.assertEqual(ut.spike_times_index[0], [0, 1, 2])
        self.assertEqual(ut.spike_times_index[1], [3, 4, 5])

    def test_get_spike_times(self):
        ut = UnitTimes('UnitTimes add_spike_times unit test')
        ut.add_spike_times(0, [0, 1, 2])
        ut.add_spike_times(1, [3, 4, 5])
        self.assertTrue(all(ut.get_unit_spike_times(0) == np.array([0, 1, 2])))
        self.assertTrue(all(ut.get_unit_spike_times(1) == np.array([3, 4, 5])))

    def test_times(self):
        ut = UnitTimes('UnitTimes add_spike_times unit test')
        ut.add_spike_times(0, [0, 1, 2])
        ut.add_spike_times(1, [3, 4, 5])
        self.assertTrue(all(ut.times[0] == np.array([0, 1, 2])))
        self.assertTrue(all(ut.times[1] == np.array([3, 4, 5])))


if __name__ == '__main__':
    unittest.main()
