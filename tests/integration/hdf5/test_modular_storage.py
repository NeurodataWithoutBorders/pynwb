import os
import gc
from datetime import datetime
from dateutil.tz import tzutc
import numpy as np

from hdmf.backends.hdf5 import HDF5IO
from hdmf.backends.hdf5.h5_utils import H5DataIO

from pynwb import get_manager, NWBFile, NWBHDF5IO, TimeSeries, validate as pynwb_validate
from pynwb.testing import remove_test_file, TestCase


class TestTimeSeriesModular(TestCase):

    def setUp(self):
        self.start_time = datetime(1971, 1, 1, 12, tzinfo=tzutc())

        self.data = np.arange(2000).reshape((2, 1000))
        self.timestamps = np.linspace(0, 1, 1000)

        self.container = TimeSeries(
            name='data_ts',
            unit='V',
            data=self.data,
            timestamps=self.timestamps
        )

        self.data_filename = os.path.join(os.getcwd(), 'test_time_series_modular_data.nwb')
        self.link_filename = os.path.join(os.getcwd(), 'test_time_series_modular_link.nwb')

        self.read_container = None
        self.link_read_io = None
        self.data_read_io = None

    def tearDown(self):
        if self.read_container:
            self.read_container.data.file.close()
            self.read_container.timestamps.file.close()
        if self.link_read_io:
            self.link_read_io.close()
        if self.data_read_io:
            self.data_read_io.close()

        # necessary to remove all references to the file and garbage
        # collect on windows in order to be able to truncate/overwrite
        # the file later. see pynwb GH issue #975
        if os.name == 'nt':
            gc.collect()

        remove_test_file(self.link_filename)
        remove_test_file(self.data_filename)

    def roundtripContainer(self):
        # create and write data file
        data_file = NWBFile(
            session_description='a test file',
            identifier='data_file',
            session_start_time=self.start_time
        )
        data_file.add_acquisition(self.container)

        with HDF5IO(self.data_filename, 'w', manager=get_manager()) as data_write_io:
            data_write_io.write(data_file)

        # read data file
        with HDF5IO(self.data_filename, 'r', manager=get_manager()) as self.data_read_io:
            data_file_obt = self.data_read_io.read()

            # write "link file" with timeseries.data that is an external link to the timeseries in "data file"
            # also link timeseries.timestamps.data to the timeseries.timestamps in "data file"
            with HDF5IO(self.link_filename, 'w', manager=get_manager()) as link_write_io:
                link_file = NWBFile(
                    session_description='a test file',
                    identifier='link_file',
                    session_start_time=self.start_time
                )
                self.link_container = TimeSeries(
                    name='test_mod_ts',
                    unit='V',
                    data=data_file_obt.get_acquisition('data_ts'),  # test direct link
                    timestamps=H5DataIO(
                        data=data_file_obt.get_acquisition('data_ts').timestamps,
                        link_data=True  # test with setting link data
                    )
                )
                link_file.add_acquisition(self.link_container)
                link_write_io.write(link_file)

        # note that self.link_container contains a link to a dataset that is now closed

        # read the link file
        self.link_read_io = HDF5IO(self.link_filename, 'r', manager=get_manager())
        self.read_nwbfile = self.link_read_io.read()
        return self.getContainer(self.read_nwbfile)

    def test_roundtrip(self):
        self.read_container = self.roundtripContainer()

        # make sure we get a completely new object
        self.assertIsNotNone(str(self.container))  # added as a test to make sure printing works
        self.assertIsNotNone(str(self.link_container))
        self.assertIsNotNone(str(self.read_container))
        self.assertFalse(self.link_container.timestamps.valid)
        self.assertTrue(self.read_container.timestamps.id.valid)
        self.assertNotEqual(id(self.link_container), id(self.read_container))
        self.assertIs(self.read_nwbfile.objects[self.link_container.object_id], self.read_container)
        self.assertContainerEqual(self.read_container, self.container, ignore_name=True, ignore_hdmf_attrs=True)
        self.assertEqual(self.read_container.object_id, self.link_container.object_id)
        self.validate()

    def test_link_root(self):
        # create and write data file
        data_file = NWBFile(
            session_description='a test file',
            identifier='data_file',
            session_start_time=self.start_time
        )
        data_file.add_acquisition(self.container)

        with HDF5IO(self.data_filename, 'w', manager=get_manager()) as data_write_io:
            data_write_io.write(data_file)

        # read data file
        manager = get_manager()
        with HDF5IO(self.data_filename, 'r', manager=manager) as data_read_io:
            data_file_obt = data_read_io.read()

            link_file = NWBFile(
                session_description='a test file',
                identifier='link_file',
                session_start_time=self.start_time
            )
            link_container = data_file_obt.acquisition[self.container.name]
            link_file.add_acquisition(link_container)
            self.assertIs(link_container.parent, data_file_obt)

            with HDF5IO(self.link_filename, 'w', manager=manager) as link_write_io:
                link_write_io.write(link_file)

        # read the link file, check container sources
        with HDF5IO(self.link_filename, 'r+', manager=get_manager()) as link_file_reader:
            read_nwbfile = link_file_reader.read()
            self.assertNotEqual(read_nwbfile.acquisition[self.container.name].container_source,
                                read_nwbfile.container_source)
            self.assertEqual(read_nwbfile.acquisition[self.container.name].container_source,
                             self.data_filename)
            self.assertEqual(read_nwbfile.container_source, self.link_filename)

    def validate(self):
        filenames = [self.data_filename, self.link_filename]
        for fn in filenames:
            if os.path.exists(fn):
                with NWBHDF5IO(fn, mode='r') as io:
                    errors = pynwb_validate(io)
                    if errors:
                        for err in errors:
                            raise Exception(err)

    def getContainer(self, nwbfile):
        return nwbfile.get_acquisition('test_mod_ts')
