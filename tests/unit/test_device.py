from pynwb.device import Device
from pynwb.testing import TestCase


class DeviceConstructorBoth(TestCase):

    def test_init(self):
        device = Device(name='device_name')

        self.assertEqual(device.name, 'device_name')
