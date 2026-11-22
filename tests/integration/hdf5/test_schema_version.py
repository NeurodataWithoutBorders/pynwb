import warnings

import h5py
import pytest

from pynwb import NWBHDF5IO, get_manager
from pynwb.testing.mock.file import mock_NWBFile


@pytest.mark.parametrize('version, expected_warning', [
    ('2.12.0-alpha', True),
    ('2.12.0-beta.1', True),
    ('2.12.0.dev1', True),
    ('2.12.0-rc1', True),
    ('2.12.0rc1', True),
    ('2.12.0', False),
    ('2.6.0-alpha', False),
])
@pytest.mark.parametrize('operation', ['write', 'export', 'read'])
def test_schema_version_warning(tmp_path, version, expected_warning, operation):
    path = tmp_path / 'test.nwb'
    manager = get_manager()
    if operation == 'write':
        manager.namespace_catalog.get_spec('core', 'NWBFile').get_attribute('nwb_version')['value'] = version
    else:
        with NWBHDF5IO(path, mode='w') as io:
            io.write(mock_NWBFile())
        with h5py.File(path, 'r+') as file:
            file.attrs['nwb_version'] = version

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        if operation == 'write':
            with NWBHDF5IO(path, mode='w', manager=manager) as io:
                io.write(mock_NWBFile())
        elif operation == 'export':
            with NWBHDF5IO(path) as src_io:
                with NWBHDF5IO(tmp_path / 'export.nwb', mode='w') as io:
                    io.export(src_io=src_io)
        else:
            with NWBHDF5IO(path) as io:
                io.read()
    schema_warnings = [w for w in caught if 'unreleased core schema' in str(w.message)]
    assert len(schema_warnings) == int(expected_warning)
    if expected_warning:
        assert version in str(schema_warnings[0].message)
        assert schema_warnings[0].category is UserWarning


@pytest.mark.parametrize('version', [None, '2.11.0', b'2.6.0-alpha'])
def test_schema_version_no_warning(version):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        NWBHDF5IO._check_schema_version(version)
    assert not caught


def test_read_skip_version_check(tmp_path):
    path = tmp_path / 'test.nwb'
    with NWBHDF5IO(path, mode='w') as io:
        io.write(mock_NWBFile())
    with h5py.File(path, 'r+') as file:
        file.attrs['nwb_version'] = '2.12.0-alpha'
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        with NWBHDF5IO(path) as io:
            io.read(skip_version_check=True)
    assert not [w for w in caught if 'unreleased core schema' in str(w.message)]
