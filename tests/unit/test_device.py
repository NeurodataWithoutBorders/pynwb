from pynwb.device import Device, DeviceModel
from pynwb.io.device import DeviceMapper
from pynwb.testing import TestCase


class DeviceBuilder(dict):

    attributes = {
        'description': 'device description',
        'manufacturer': 'manufacturer',
        'model_number': 'model_number',
    }


class TestDevice(TestCase):

    def test_init(self):
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

        self.assertEqual(device.name, 'device_name')
        self.assertEqual(device.description, 'description')
        self.assertEqual(device.serial_number, 'serial_number')
        self.assertIs(device.model, device_model)

    def test_deprecated_manufacturer(self):
        msg = (
            "The 'manufacturer' field is deprecated. Instead, use DeviceModel.manufacturer and link to that "
            "DeviceModel from this Device."
        )
        with self.assertWarnsWith(DeprecationWarning, msg):
            device = Device(
                name='device_name',
                description='description',
                manufacturer='manufacturer',
            )
        self.assertEqual(device.manufacturer, 'manufacturer')

    def test_deprecated_model_number(self):
        msg = (
            "The 'model_number' field is deprecated. Instead, use DeviceModel.model_number and link to that "
            "DeviceModel from this Device."
        )
        with self.assertWarnsWith(DeprecationWarning, msg):
            device = Device(
                name='device_name',
                description='description',
                model_number='model_number',
            )
        self.assertEqual(device.model_number, 'model_number')

    def test_deprecated_model_name(self):
        msg = (
            "The 'model_name' field is deprecated. Instead, use DeviceModel.name and link to that "
            "DeviceModel from this Device."
        )
        with self.assertWarnsWith(DeprecationWarning, msg):
            device = Device(
                name='device_name',
                description='description',
                model_name='model_name',
            )
        self.assertEqual(device.model_name, 'model_name')


class TestDeviceModel(TestCase):

    def test_init(self):
        device_model = DeviceModel(
            name='device_model_name',
            manufacturer='manufacturer',
            model_number='model_number',
            description='description',
        )

        self.assertEqual(device_model.name, 'device_model_name')
        self.assertEqual(device_model.manufacturer, 'manufacturer')
        self.assertEqual(device_model.model_number, 'model_number')
        self.assertEqual(device_model.description, 'description')


class TestDeviceMapper(TestCase):

    def test_model_carg_preserves_legacy_model_name(self):
        builder = DeviceBuilder(model='MFC_200/250-0.66_40mm_MF2.5:FLT')
        msg = (
            'Device.model was detected as a string, but NWB 2.9 specifies Device.model as a link to a DeviceModel. '
            'Remapping "MFC_200/250-0.66_40mm_MF2.5:FLT" to a new DeviceModel.'
        )
        with self.assertWarnsWith(UserWarning, msg):
            device_model = DeviceMapper.model_carg(None, builder, None)

        self.assertIsInstance(device_model, DeviceModel)
        self.assertEqual(device_model.name, 'MFC_200/250-0.66_40mm_MF2.5:FLT')
        self.assertEqual(device_model.description, 'device description')
        self.assertEqual(device_model.manufacturer, 'manufacturer')
        self.assertEqual(device_model.model_number, 'model_number')
