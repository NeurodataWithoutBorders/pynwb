import unittest

from pynwb.device import Device


class DeviceConstructorBoth(unittest.TestCase):

    def test_init(self):
        device = Device(name='device_name', source='device_source')

        self.assertEqual(device.name, 'device_name')
        self.assertEqual(device.source, 'device_source')
