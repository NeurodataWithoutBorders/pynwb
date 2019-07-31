import unittest

from pynwb.device import Device


class DeviceConstructorBoth(unittest.TestCase):

    def test_init(self):
        device = Device(name='device_name')

        self.assertEqual(device.name, 'device_name')
