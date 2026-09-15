from pynwb.ogen import OptogeneticSeries, OptogeneticStimulusSite
from pynwb.ecephys import Device
from pynwb.testing import TestCase


class OptogeneticSeriesConstructor(TestCase):

    def test_init(self):
        device = Device('name')
        oS = OptogeneticStimulusSite('site1', device, 'description', 300., 'location')
        self.assertEqual(oS.name, 'site1')
        self.assertEqual(oS.device, device)
        self.assertEqual(oS.description, 'description')
        self.assertEqual(oS.excitation_lambda, 300.)
        self.assertEqual(oS.location, 'location')

        iS = OptogeneticSeries('test_iS', list(), oS, timestamps=list())
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.unit, 'watts')
        self.assertEqual(iS.site, oS)
