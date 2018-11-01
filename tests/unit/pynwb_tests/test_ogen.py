import unittest

from pynwb.ogen import OptogeneticSeries, OptogeneticStimulusSite
from pynwb.ecephys import Device


class OptogeneticSeriesConstructor(unittest.TestCase):

    def test_init(self):
        device = Device('name')
        oS = OptogeneticStimulusSite('site1', device, 'description', 'excitation_lambda', 'location')
        self.assertEqual(oS.name, 'site1')
        self.assertEqual(oS.device, device)
        self.assertEqual(oS.description, 'description')
        self.assertEqual(oS.excitation_lambda, 'excitation_lambda')
        self.assertEqual(oS.location, 'location')

        iS = OptogeneticSeries('test_iS', list(), oS, timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.unit, 'Watt')
        self.assertEqual(iS.site, oS)


if __name__ == '__main__':
    unittest.main()
