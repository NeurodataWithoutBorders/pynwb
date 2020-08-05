from pynwb.ogen import OptogeneticSeries, OptogeneticStimulusSite
from pynwb.ecephys import Device
from pynwb.testing import TestCase


class OptogeneticSeriesConstructor(TestCase):

    def test_init(self):
        device = Device('name')
        oS = OptogeneticStimulusSite(
            name='site1',
            device=device,
            description='description',
            excitation_lambda=300.,
            location='location'
        )
        self.assertEqual(oS.name, 'site1')
        self.assertEqual(oS.device, device)
        self.assertEqual(oS.description, 'description')
        self.assertEqual(oS.excitation_lambda, 300.)
        self.assertEqual(oS.location, 'location')

        iS = OptogeneticSeries(
            name='test_iS',
            data=[1, 2, 3],
            site=oS,
            timestamps=[0.1, 0.2, 0.3]
        )
        self.assertEqual(iS.name, 'test_iS')
        self.assertEqual(iS.unit, 'watts')
        self.assertEqual(iS.site, oS)
