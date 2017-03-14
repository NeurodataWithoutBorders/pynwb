import unittest

from pynwb import TimeSeries
from pynwb.ogen import OptogeneticSeries, OptogeneticSite

import numpy as np


class OptogeneticSeriesConstructor(unittest.TestCase):

    def test_init(self):
        iS = OptogeneticSeries('test_iS', 'a hypothetical source', list(), 'site', timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.source, 'a hypothetical source')
        self.assertEqual(iS.unit, 'Watt')
        self.assertEqual(iS.site, 'site')


class OptogeneticSiteConstructor(unittest.TestCase):

    def test_init(self):
        pass

