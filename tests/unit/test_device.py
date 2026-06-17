from pynwb import NWBHDF5IO
from pynwb.device import Device, DeviceModel
from pynwb.io.device import DeviceMapper, DEVICE_MODEL_TUTORIAL_URL, _construct_legacy_device_model
from pynwb.testing import TestCase, remove_test_file
from pynwb.testing.mock.file import mock_NWBFile


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

    def test_model_carg_remaps_valid_legacy_model_name(self):
        builder = DeviceBuilder(model='valid_model_name')
        msg = (
            'Device.model was detected as a string, but NWB 2.9 specifies Device.model as a link to a DeviceModel. '
            'Remapping "valid_model_name" to a new DeviceModel.'
        )
        with self.assertWarnsWith(UserWarning, msg):
            device_model = DeviceMapper.model_carg(None, builder, None)

        self.assertIsInstance(device_model, DeviceModel)
        self.assertEqual(device_model.name, 'valid_model_name')
        self.assertEqual(device_model.description, 'device description')
        self.assertEqual(device_model.manufacturer, 'manufacturer')
        self.assertEqual(device_model.model_number, 'model_number')

    def test_model_carg_preserves_invalid_legacy_model_name(self):
        builder = DeviceBuilder(model='MFC_200/250-0.66_40mm_MF2.5:FLT')
        msg = (
            'Device.model was detected as a string, but NWB 2.9 specifies Device.model as a link to a DeviceModel. '
            'Remapping "MFC_200/250-0.66_40mm_MF2.5:FLT" to a new DeviceModel. '
            'Because the model name contains a "/" or ":", which are not allowed in NWB object names, the '
            'remapped DeviceModel is read-only and the file cannot be written or exported until it is '
            'replaced. To write/export the data, create a new DeviceModel with a valid name and assign it to '
            'Device.model. See ' + DEVICE_MODEL_TUTORIAL_URL + ' for an example.'
        )
        with self.assertWarnsWith(UserWarning, msg):
            device_model = DeviceMapper.model_carg(None, builder, None)

        self.assertIsInstance(device_model, DeviceModel)
        self.assertEqual(device_model.name, 'MFC_200/250-0.66_40mm_MF2.5:FLT')
        self.assertEqual(device_model.description, 'device description')
        self.assertEqual(device_model.manufacturer, 'manufacturer')
        self.assertEqual(device_model.model_number, 'model_number')


class TestDeviceModelWriteGuard(TestCase):
    """The read-only DeviceModel remapped from a legacy invalid string cannot be written or exported."""

    def setUp(self):
        self.filename = 'test_device_model_write_guard.nwb'

    def tearDown(self):
        remove_test_file(self.filename)

    def test_write_invalid_device_model_name_raises(self):
        device_model = _construct_legacy_device_model(
            name='MFC_200/250-0.66_40mm_MF2.5:FLT',
            manufacturer='manufacturer',
            model_number='model_number',
            description='description',
        )
        nwbfile = mock_NWBFile()
        nwbfile.add_device_model(device_model)
        nwbfile.add_device(Device(name='device_name', description='description', model=device_model))

        msg = (
            'Cannot write DeviceModel "MFC_200/250-0.66_40mm_MF2.5:FLT": its name contains a "/" or ":", '
            'which are not allowed in NWB object names. This DeviceModel was likely remapped '
            'from a legacy Device.model string when reading an older file and is read-only. To '
            'write or export the data, create a new DeviceModel with a valid name and assign it to '
            'Device.model. See ' + DEVICE_MODEL_TUTORIAL_URL + ' for an example.'
        )
        with NWBHDF5IO(self.filename, 'w') as io:
            with self.assertRaisesWith(ValueError, msg):
                io.write(nwbfile)

    def test_write_valid_remapped_device_model_name_succeeds(self):
        device_model = _construct_legacy_device_model(
            name='valid_model_name',
            manufacturer='manufacturer',
            model_number='model_number',
            description='description',
        )
        nwbfile = mock_NWBFile()
        nwbfile.add_device_model(device_model)
        nwbfile.add_device(Device(name='device_name', description='description', model=device_model))

        with NWBHDF5IO(self.filename, 'w') as io:
            io.write(nwbfile)

        with NWBHDF5IO(self.filename, 'r') as io:
            read_nwbfile = io.read()
            self.assertEqual(read_nwbfile.devices['device_name'].model.name, 'valid_model_name')
