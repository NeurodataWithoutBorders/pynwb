from pynwb.device import Device
from pynwb.testing import TestCase


class TestDevice(TestCase):

    def test_init(self):
        device = Device(
            name='device_name',
            description='description',
            manufacturer='manufacturer',
            model_number='model_number',
            model_name='model_name',
            serial_number='serial_number',
        )

        self.assertEqual(device.name, 'device_name')
        self.assertEqual(device.description, 'description')
        self.assertEqual(device.manufacturer, 'manufacturer')
        self.assertEqual(device.model_number, 'model_number')
        self.assertEqual(device.model_name, 'model_name')
        self.assertEqual(device.serial_number, 'serial_number')
