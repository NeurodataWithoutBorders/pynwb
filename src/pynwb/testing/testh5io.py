from datetime import datetime
from dateutil.tz import tzlocal, tzutc
import os
from abc import ABCMeta, abstractmethod
import warnings

from pynwb import NWBFile, NWBHDF5IO, validate as pynwb_validate
from .utils import remove_test_file
from hdmf.backends.warnings import BrokenLinkWarning
from hdmf.build.warnings import MissingRequiredWarning, OrphanContainerWarning


class NWBH5IOMixin(metaclass=ABCMeta):
    """
    Mixin class for methods to run a roundtrip test writing an NWB file with an Container and reading the Container
    from the NWB file. The setUp, test_roundtrip, and tearDown methods will be run by unittest.

    The abstract methods setUpContainer, addContainer, and getContainer needs to be implemented by classes that include
    this mixin.

    Example::

        class TestMyContainerIO(NWBH5IOMixin, TestCase):
            def setUpContainer(self):
                # return a test Container to read/write
            def addContainer(self, nwbfile):
                # add the test Container to an NWB file
            def getContainer(self, nwbfile):
                # return the test Container from an NWB file

    This code is adapted from hdmf.testing.H5RoundTripMixin.
    """

    def setUp(self):
        self.container = self.setUpContainer()
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

    @abstractmethod
    def setUpContainer(self):
        """ Should return the test Container to read/write """
        raise NotImplementedError('Cannot run test unless setUpContainer is implemented')

    def test_roundtrip(self):
        """
        Test whether the test Container read from file has the same contents as the original test Container and
        validate the file
        """
        self.read_container = self.roundtripContainer()
        self.assertIsNotNone(str(self.container))  # added as a test to make sure printing works
        self.assertIsNotNone(str(self.read_container))
        # make sure we get a completely new object
        self.assertNotEqual(id(self.container), id(self.read_container))
        self.assertIs(self.read_nwbfile.objects[self.container.object_id], self.read_container)
        self.assertContainerEqual(self.read_container, self.container)

    def roundtripContainer(self, cache_spec=False):
        """
        Add the test Container to an NWBFile, write it to file, read the file, and return the test Container from the
        file
        """
        description = 'a file to test writing and reading a %s' % self.container_type
        identifier = 'TEST_%s' % self.container_type
        nwbfile = NWBFile(description, identifier, self.start_time, file_create_date=self.create_date)
        self.addContainer(nwbfile)

        with warnings.catch_warnings(record=True) as ws:
            self.writer = NWBHDF5IO(self.filename, mode='w')
            self.writer.write(nwbfile, cache_spec=cache_spec)
            self.writer.close()

            self.validate()

            self.reader = NWBHDF5IO(self.filename, mode='r')
            self.read_nwbfile = self.reader.read()

        if ws:
            for w in ws:
                if issubclass(w.category, (MissingRequiredWarning,
                                           OrphanContainerWarning,
                                           BrokenLinkWarning)):
                    raise Exception('%s: %s' % (w.category.__name__, w.message))
                else:
                    warnings.warn(w.message, w.category)

        try:
            return self.getContainer(self.read_nwbfile)
        except Exception as e:
            self.reader.close()
            self.reader = None
            raise e

    @abstractmethod
    def addContainer(self, nwbfile):
        """ Should add the test Container to the given NWBFile """
        raise NotImplementedError('Cannot run test unless addContainer is implemented')

    @abstractmethod
    def getContainer(self, nwbfile):
        """ Should return the test Container from the given NWBFile """
        raise NotImplementedError('Cannot run test unless getContainer is implemented')

    def validate(self):
        """ Validate the created file """
        if os.path.exists(self.filename):
            with NWBHDF5IO(self.filename, mode='r') as io:
                errors = pynwb_validate(io)
                if errors:
                    for err in errors:
                        raise Exception(err)


class AcquisitionH5IOMixin(NWBH5IOMixin):
    """
    Mixin class for methods to run a roundtrip test writing an NWB file with an Container as an acquisition and reading
    the Container as an acquisition from the NWB file. The setUp, test_roundtrip, and tearDown methods will be run by
    unittest.

    The abstract method setUpContainer needs to be implemented by classes that include this mixin.

    Example::

        class TestMyContainerIO(NWBH5IOMixin, TestCase):
            def setUpContainer(self):
                # return a test Container to read/write

    This code is adapted from hdmf.testing.H5RoundTripMixin.
    """

    def addContainer(self, nwbfile):
        ''' Add an NWBDataInterface object to the file as an acquisition '''
        nwbfile.add_acquisition(self.container)

    def getContainer(self, nwbfile):
        ''' Get the NWBDataInterface object from the file '''
        return nwbfile.get_acquisition(self.container.name)
