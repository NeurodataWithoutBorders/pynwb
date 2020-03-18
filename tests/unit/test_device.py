from pynwb.device import Device
from pynwb.testing import TestCase


class TestDevice(TestCase):

    def test_init(self):
        device = Device(name='device_name',
                        description='description',
                        manufacturer='manufacturer')

        self.assertEqual(device.name, 'device_name')
        self.assertEqual(device.description, 'description')
        self.assertEqual(device.manufacturer, 'manufacturer')
