import unittest

from pynwb.ogen import OptogeneticSeries, OptogeneticStimulusSite


class OptogeneticSeriesConstructor(unittest.TestCase):

    def test_init(self):
        oS = OptogeneticStimulusSite('site1', 'a test source', 'device', 'description', 'excitation_lambda', 'location')
        self.assertEqual(oS.name, 'site1')
        self.assertEqual(oS.device, 'device')
        self.assertEqual(oS.description, 'description')
        self.assertEqual(oS.excitation_lambda, 'excitation_lambda')
        self.assertEqual(oS.location, 'location')

        iS = OptogeneticSeries('test_iS', 'a hypothetical source', list(), oS, timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.source, 'a hypothetical source')
        self.assertEqual(iS.unit, 'Watt')
        self.assertEqual(iS.site, oS)


if __name__ == '__main__':
    unittest.main()
