import unittest

from pynwb import TimeSeries
from pynwb.ogen import OptogeneticSeries, OptogeneticStimulusSite

import numpy as np


class OptogeneticSeriesConstructor(unittest.TestCase):

    def test_init(self):
        oS = OptogeneticStimulusSite()

        iS = OptogeneticSeries('test_iS', 'a hypothetical source', list(), oS, timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.source, 'a hypothetical source')
        self.assertEqual(iS.unit, 'Watt')
        self.assertEqual(iS.site, oS)


class OptogeneticSiteConstructor(unittest.TestCase):

    def test_init(self):
        pass

if __name__ == '__main__':
    unittest.main()

