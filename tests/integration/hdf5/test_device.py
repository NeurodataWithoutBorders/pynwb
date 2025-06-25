from pynwb.device import Device, DeviceModel
from pynwb.testing import NWBH5IOMixin, TestCase


class TestDeviceIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test Device to read/write """
        device_model = DeviceModel(
            name='device_model_name',
            manufacturer='manufacturer',
            model_number='model_number',
            description='description',
        )
        device = Device(
            name='device_name',
            description='description',
            serial_number='serial_number',
            model=device_model,
        )
        return device

    def addContainer(self, nwbfile):
        """ Add the test Device to the given NWBFile """
        nwbfile.add_device(self.container)
        nwbfile.add_device_model(self.container.model)

    def getContainer(self, nwbfile):
        """ Return the test Device from the given NWBFile """
        return nwbfile.get_device(self.container.name)


class TestDeviceModelIO(NWBH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test DeviceModel to read/write """
        device_model = DeviceModel(
            name='device_model_name',
            manufacturer='manufacturer',
            model_number='model_number',
            description='description',
        )
        return device_model

    def addContainer(self, nwbfile):
        """ Add the test DeviceModel to the given NWBFile """
        nwbfile.add_device_model(self.container)

    def getContainer(self, nwbfile):
        """ Return the test DeviceModel from the given NWBFile """
        return nwbfile.get_device_model(self.container.name)
