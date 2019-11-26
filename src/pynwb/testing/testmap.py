import unittest
from datetime import datetime
from dateutil.tz import tzlocal, tzutc
import os

from pynwb import get_manager, NWBFile, NWBHDF5IO, validate as pynwb_validate
from .utils import remove_test_file
from hdmf.testing import TestCase
from hdmf.backends.hdf5 import HDF5IO


class TestMapNWBContainer(TestCase):

    _required_tests = tuple()

    def setUp(self):
        self.__manager = get_manager()
        self.container = self.setUpContainer()

    @property
    def required_tests(self):
        return self._required_tests

    @property
    def manager(self):
        return self.__manager

    def setUpBuilder(self):
        ''' Should return the Builder that represents the Container'''
        raise unittest.SkipTest('Cannot run test unless setUpBuilder is implemented')

    def setUpContainer(self):
        ''' Should return the Container to build and read/write'''
        raise unittest.SkipTest('Cannot run test unless setUpContainer is implemented')


class TestMapRoundTrip(TestMapNWBContainer):

    _required_tests = ('test_roundtrip',)
    run_injected_file_test = False

    def setUp(self):
        super(TestMapRoundTrip, self).setUp()
        self.object_id = self.container.object_id
        self.start_time = datetime(1971, 1, 1, 12, tzinfo=tzutc())
        self.create_date = datetime(2018, 4, 15, 12, tzinfo=tzlocal())
        self.container_type = self.container.__class__.__name__
        self.filename = 'test_%s.nwb' % self.container_type
        self.writer = None
        self.reader = None

    def tearDown(self):
        if self.writer is not None:
            self.writer.close()
        if self.reader is not None:
            self.reader.close()
        remove_test_file(self.filename)

    def roundtripContainer(self, cache_spec=False):
        description = 'a file to test writing and reading a %s' % self.container_type
        identifier = 'TEST_%s' % self.container_type
        nwbfile = NWBFile(description, identifier, self.start_time, file_create_date=self.create_date)
        self.addContainer(nwbfile)

        self.writer = HDF5IO(self.filename, manager=get_manager(), mode='w')
        self.writer.write(nwbfile, cache_spec=cache_spec)
        self.writer.close()
        self.reader = HDF5IO(self.filename, manager=get_manager(), mode='r')
        self.read_nwbfile = self.reader.read()

        try:
            tmp = self.getContainer(self.read_nwbfile)
            return tmp
        except Exception as e:
            self.reader.close()
            self.reader = None
            raise e

    def test_roundtrip(self):
        self.read_container = self.roundtripContainer()
        # make sure we get a completely new object
        self.assertIsNotNone(str(self.container))  # added as a test to make sure printing works
        self.assertIsNotNone(str(self.read_container))
        self.assertNotEqual(id(self.container), id(self.read_container))
        self.assertIs(self.read_nwbfile.objects[self.container.object_id], self.read_container)
        self.assertContainerEqual(self.read_container, self.container)
        self.validate()

    def validate(self):
        # validate created file
        if os.path.exists(self.filename):
            with NWBHDF5IO(self.filename, mode='r') as io:
                errors = pynwb_validate(io)
                if errors:
                    for err in errors:
                        raise Exception(err)

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        raise unittest.SkipTest('Cannot run test unless addContainer is implemented')

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        raise unittest.SkipTest('Cannot run test unless getContainer is implemented')


class TestDataInterfaceIO(TestMapRoundTrip):

    def addContainer(self, nwbfile):
        ''' Should take an NWBFile object and add the container to it '''
        nwbfile.add_acquisition(self.container)

    def getContainer(self, nwbfile):
        ''' Should take an NWBFile object and return the Container'''
        return nwbfile.get_acquisition(self.container.name)
