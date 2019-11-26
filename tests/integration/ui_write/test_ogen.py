from pynwb.ogen import OptogeneticSeries, OptogeneticStimulusSite
from pynwb.device import Device
from pynwb.testing import TestMapRoundTrip


class TestOptogeneticStimulusSite(TestMapRoundTrip):

    def setUpContainer(self):
        self.device = Device(name='dev1')
        return OptogeneticStimulusSite('stim_site', self.device, 'my stim site', 300., 'in the brain')

    def addContainer(self, nwbfile):
        nwbfile.add_device(self.device)
        nwbfile.add_ogen_site(self.container)

    def getContainer(self, nwbfile):
        return nwbfile.get_ogen_site(self.container.name)


class TestOptogeneticStimulusSeries(TestMapRoundTrip):
    """
    A TestCase class for testing OptogeneticStimulusSeries
    """

    def setUpContainer(self):
        self.device = Device(name='dev1')
        self.ogen_stim_site = OptogeneticStimulusSite('stim_site', self.device, 'my stim site', 300., 'in the brain')
        return OptogeneticSeries('stim_series', [1., 2., 3.], self.ogen_stim_site, rate=100.)

    def addContainer(self, nwbfile):
        nwbfile.add_device(self.device)
        nwbfile.add_ogen_site(self.ogen_stim_site)
        nwbfile.add_acquisition(self.container)
