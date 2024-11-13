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
        # File paths
        self.data_filename = os.path.join(os.getcwd(), 'test_time_series_modular_data.nwb')
        self.link_filename = os.path.join(os.getcwd(), 'test_time_series_modular_link.nwb')

        # Make the data container file write
        self.start_time = datetime(1971, 1, 1, 12, tzinfo=tzutc())
        self.data = np.arange(2000).reshape((1000, 2))
        self.timestamps = np.linspace(0, 1, 1000)
        # The container before roundtrip
        self.container = TimeSeries(
            name='data_ts',
            unit='V',
            data=self.data,
            timestamps=self.timestamps
        )
        self.data_read_io = None          # HDF5IO used for reading the main data file
        self.read_data_nwbfile = None     # The NWBFile read after roundtrip
        self.read_data_container = None   # self.container after roundtrip

        # Variables for the second file which links the main data file
        self.link_container = None        # The container with the links before write
        self.read_link_container = None   # The container with the links after roundtrip
        self.read_link_nwbfile = None     # The NWBFile container containing link_container after roundtrip
        self.link_read_io = None          # HDF5IO use for reading the read_link_nwbfile

    def tearDown(self):
        if self.read_link_container:
            self.read_link_container.data.file.close()
            self.read_link_container.timestamps.file.close()
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
        self.data_read_io = HDF5IO(self.data_filename, 'r', manager=get_manager())
        self.read_data_nwbfile = self.data_read_io.read()
        self.read_data_container = self.read_data_nwbfile.get_acquisition('data_ts')

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
                data=H5DataIO(
                    data=self.read_data_container.data,
                    link_data=True  # test with setting link data
                ),
                timestamps=H5DataIO(
                    data=self.read_data_container.timestamps,
                    link_data=True  # test with setting link data
                )
            )
            link_file.add_acquisition(self.link_container)
            link_write_io.write(link_file)

        # read the link file
        self.link_read_io = HDF5IO(self.link_filename, 'r', manager=get_manager())
        self.read_link_nwbfile = self.link_read_io.read()
        return self.getContainer(self.read_link_nwbfile)

    def test_roundtrip(self):
        # Roundtrip the container
        self.read_link_container = self.roundtripContainer()

        # 1. Make sure our containers are set correctly for the test
        # 1.1:  Make sure the container we read is not identical to the container we used for writing
        self.assertNotEqual(id(self.link_container), id(self.read_link_container))
        self.assertNotEqual(id(self.container), id(self.read_data_container))
        # 1.2: Make sure the container we read is indeed the correct container we should use for testing
        self.assertIs(self.read_link_nwbfile.objects[self.link_container.object_id], self.read_link_container)
        self.assertIs(self.read_data_nwbfile.objects[self.container.object_id], self.read_data_container)
        # 1.3: Make sure the object_ids of the container we wrote and read are the same
        self.assertEqual(self.read_link_container.object_id, self.link_container.object_id)
        self.assertEqual(self.read_data_container.object_id, self.container.object_id)
        # 1.4: Make sure the object_ids between the source data and link data container are different
        self.assertNotEqual(self.read_link_container.object_id, self.read_data_container.object_id)

        # Test that printing works for the source data and linked data container
        self.assertIsNotNone(str(self.container))
        self.assertIsNotNone(str(self.read_data_container))
        self.assertIsNotNone(str(self.link_container))
        self.assertIsNotNone(str(self.read_link_container))

        # Test that timestamps and data are valid after write
        self.assertTrue(self.read_link_container.timestamps.id.valid)
        self.assertTrue(self.read_link_container.data.id.valid)
        self.assertTrue(self.read_data_container.timestamps.id.valid)
        self.assertTrue(self.read_data_container.data.id.valid)

        # Make sure the data in the read data container and linked data container match the original container
        self.assertContainerEqual(self.read_link_container, self.container, ignore_name=True, ignore_hdmf_attrs=True)
        self.assertContainerEqual(self.read_data_container, self.container, ignore_name=True, ignore_hdmf_attrs=True)

        # Make sure the timestamps and data are linked correctly. I.e., the filename of the h5py dataset should
        # match between the data file and the file with links even-though they have been read from different files
        self.assertEqual(
            self.read_data_container.data.file.filename,  # Path where the source data is stored
            self.read_link_container.data.file.filename   # Path where the linked h5py dataset points to
        )
        self.assertEqual(
            self.read_data_container.timestamps.file.filename,  # Path where the source data is stored
            self.read_link_container.timestamps.file.filename   # Path where the linked h5py dataset points to
        )

        # validate both the source data and linked data file via the pynwb validator
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


class TestTimeSeriesModularLinkViaTimeSeries(TestTimeSeriesModular):
    """
    Same as TestTimeSeriesModular but creating links by setting TimeSeries.data
    and TimeSeries.timestamps to the other TimeSeries on construction, rather than
    using H5DataIO.
    """
    def setUp(self):
        super().setUp()
        self.skipTest("This behavior is currently broken. See issue .")

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
        self.data_read_io = HDF5IO(self.data_filename, 'r', manager=get_manager())
        self.read_data_nwbfile = self.data_read_io.read()
        self.read_data_container = self.read_data_nwbfile.get_acquisition('data_ts')

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
                data=self.read_data_container,       # <--- This is the main difference to TestTimeSeriesModular
                timestamps=self.read_data_container  # <--- This is the main difference to TestTimeSeriesModular
            )
            link_file.add_acquisition(self.link_container)
            link_write_io.write(link_file)

        # note that self.link_container contains a link to a dataset that is now closed

        # read the link file
        self.link_read_io = HDF5IO(self.link_filename, 'r', manager=get_manager())
        self.read_link_nwbfile = self.link_read_io.read()
        return self.getContainer(self.read_link_nwbfile)
