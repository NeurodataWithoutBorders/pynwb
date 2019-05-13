import os
import tempfile
import shutil
import unittest
from datetime import datetime
from dateutil.tz import tzutc

import numpy as np

from pynwb.base import TimeSeries
from pynwb import get_manager, NWBFile
from hdmf.backends.hdf5 import HDF5IO
from hdmf.backends.hdf5.h5_utils import H5DataIO

from . import base


class TestTimeSeriesModular(base.TestMapRoundTrip):

    _required_tests = ('test_roundtrip',)

    def remove_file(self, path):
        if os.path.exists(path) and os.getenv("CLEAN_NWB", '1') not in ('0', 'false', 'FALSE', 'False'):
            os.remove(path)

    def setUp(self):
        self.__manager = get_manager()
        self.start_time = datetime(1971, 1, 1, 12, tzinfo=tzutc())

        self.data = np.arange(2000).reshape((2, 1000))
        self.timestamps = np.linspace(0, 1, 1000)

        self.container = TimeSeries(
            name='data_ts',
            unit='V',
            data=self.data,
            timestamps=self.timestamps
        )

        self.data_filename = 'test_time_series_modular_data.nwb'
        self.link_filename = 'test_time_series_modular_link.nwb'

    def tearDown(self):
        self.read_container.data.file.close()
        self.read_container.timestamps.file.close()

        self.remove_file(self.data_filename)
        self.remove_file(self.link_filename)

    def roundtripContainer(self):
        data_file = NWBFile(
            session_description='a test file',
            identifier='data_file',
            session_start_time=self.start_time
        )
        data_file.add_acquisition(self.container)

        with HDF5IO(self.data_filename, 'w', manager=get_manager()) as self.data_write_io:
            self.data_write_io.write(data_file)

        with HDF5IO(self.data_filename, 'r', manager=get_manager()) as self.data_read_io:
            data_file_obt = self.data_read_io.read()

            with HDF5IO(self.link_filename, 'w', manager=get_manager()) as link_write_io:
                link_file = NWBFile(
                    session_description='a test file',
                    identifier='link_file',
                    session_start_time=self.start_time
                )
                link_file.add_acquisition(TimeSeries(
                    name='test_mod_ts',
                    unit='V',
                    data=data_file_obt.get_acquisition('data_ts'),
                    timestamps=H5DataIO(
                        data=data_file_obt.get_acquisition('data_ts').timestamps,
                        link_data=True
                    )
                ))
                link_write_io.write(link_file)

        with HDF5IO(self.link_filename, 'r', manager=get_manager()) as self.link_file_reader:
            return self.getContainer(self.link_file_reader.read())

    def getContainer(self, nwbfile):
        return nwbfile.get_acquisition('test_mod_ts')

    def addContainer(self, nwbfile):
        pass


class TestMissingLink(base.TestMapNWBContainer):

    _required_tests = ('test_roundtrip', 'test_missing')

    @property
    def data(self):
        return np.arange(50)

    @property
    def timestamps(self):
        return np.linspace(0, 1, 50)

    def setUp(self):
        self.dirname = tempfile.mkdtemp()
        self.data_filename = os.path.join(self.dirname, 'data.nwb')
        self.link_filename = os.path.join(self.dirname, 'link.nwb')

        self.data_file = NWBFile(
            session_description='a test file',
            identifier='data_file',
            session_start_time=datetime.now()
        )
        self.data_file.add_acquisition(self.timeseries())

        with HDF5IO(self.data_filename, 'w', manager=get_manager()) as data_write_io:
            data_write_io.write(self.data_file)

        with HDF5IO(self.data_filename, 'r', manager=get_manager()) as data_read_io:
            data_file = data_read_io.read()

            with HDF5IO(self.link_filename, 'w', manager=get_manager()) as link_write_io:
                link_file = NWBFile(
                    session_description='a test file',
                    identifier='link_file',
                    session_start_time=datetime.now()
                )
                link_file.add_acquisition(TimeSeries(
                    name='test_mod_ts',
                    unit='V',
                    data=data_file.get_acquisition('data_ts'),
                    timestamps=H5DataIO(
                        data=data_file.get_acquisition('data_ts').timestamps,
                        link_data=True
                    )
                ))
                link_write_io.write(link_file)

    def timeseries(self):
        return TimeSeries(
            name='data_ts',
            unit='V',
            data=self.data,
            timestamps=self.timestamps
        )

    def tearDown(self):
        shutil.rmtree(self.dirname)

    def test_roundtrip(self):
        expected = self.timeseries()

        with HDF5IO(self.link_filename, 'r', manager=get_manager()) as link_io:
            read_fil = link_io.read()
            obtained = read_fil.get_acquisition('test_mod_ts')

            self.assertNotEqual(id(expected), id(obtained))
            self.assertContainerEqual(expected, obtained)

    def test_missing(self):
        
        tmp_data_filename = os.path.join(self.dirname, '_data.nwb')
        shutil.move(self.data_filename, tmp_data_filename)

        with HDF5IO(self.link_filename, 'r', manager=get_manager()) as link_io:
            read_fil = link_io.read()
            obtained = read_fil.get_acquisition('test_mod_ts')
