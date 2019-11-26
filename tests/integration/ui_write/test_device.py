from pynwb.device import Device
from pynwb.testing import TestMapRoundTrip


class TestDevice(TestMapRoundTrip):

    def setUpContainer(self):
        self.device = Device(name='device_name')
        return self.device

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_device(self.device)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_device(self.device.name)
