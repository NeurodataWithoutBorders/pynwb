import unittest

from pynwb.device import Device


class DeviceConstructorBoth(unittest.TestCase):

    def test_init(self):
        device = Device(name='device_name', description='a mock device for testing')

        self.assertEqual(device.name, 'device_name')
