from pynwb.device import Device

from . import base


class TestDevice(base.TestMapRoundTrip):

    def setUpContainer(self):
        self.device = Device(name='device_name')
        return self.device

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_device(self.device)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_device(self.device.name)
