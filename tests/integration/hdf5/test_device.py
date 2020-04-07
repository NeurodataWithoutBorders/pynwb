from pynwb.device import Device
from pynwb.testing import NWBH5IOMixin, TestCase


class TestDeviceIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test Device to read/write """
        return Device(name='device_name',
                      description='description',
                      manufacturer='manufacturer')

    def addContainer(self, nwbfile):
        """ Add the test Device to the given NWBFile """
        nwbfile.add_device(self.container)

    def getContainer(self, nwbfile):
        """ Return the test Device from the given NWBFile """
        return nwbfile.get_device(self.container.name)
