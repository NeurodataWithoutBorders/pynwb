from datetime import datetime
from dateutil.tz import tzlocal, tzutc
import os
from abc import ABCMeta, abstractmethod
import warnings

from pynwb import NWBFile, NWBHDF5IO, get_manager, validate as pynwb_validate
from .utils import remove_test_file
from hdmf.backends.warnings import BrokenLinkWarning
from hdmf.build.warnings import MissingRequiredBuildWarning


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
        self.export_filename = 'test_export_%s.nwb' % self.container_type
        self.reader = None
        self.export_reader = None

    def tearDown(self):
        if self.reader is not None:
            self.reader.close()
        if self.export_reader is not None:
            self.export_reader.close()
        remove_test_file(self.filename)
        remove_test_file(self.export_filename)

    @abstractmethod
    def setUpContainer(self):
        """ Should return the test Container to read/write """
        raise NotImplementedError('Cannot run test unless setUpContainer is implemented')

    def test_roundtrip(self):
        """Test whether the read Container has the same contents as the original Container and validate the file.
        """
        self.read_container = self.roundtripContainer()
        self.assertIsNotNone(str(self.container))  # added as a test to make sure printing works
        self.assertIsNotNone(str(self.read_container))
        # make sure we get a completely new object
        self.assertNotEqual(id(self.container), id(self.read_container))
        # make sure the object ID is preserved
        self.assertIs(self.read_nwbfile.objects[self.container.object_id], self.read_container)
        self.assertContainerEqual(self.read_container, self.container)

    def test_roundtrip_export(self):
        """
        Test whether the test Container read from an exported file has the same contents as the original test Container
        and validate the file
        """
        self.read_container = self.roundtripExportContainer()
        self.assertIsNotNone(str(self.read_container))  # added as a test to make sure printing works
        # make sure we get a completely new object
        self.assertNotEqual(id(self.container), id(self.read_container))
        # make sure the object ID is preserved
        self.assertIs(self.read_exported_nwbfile.objects[self.container.object_id], self.read_container)
        self.assertContainerEqual(self.read_container, self.container, ignore_hdmf_attrs=True)

    def roundtripContainer(self, cache_spec=True):
        """Add the Container to an NWBFile, write it to file, read the file, and return the Container from the file.
        """
        session_description = 'a file to test writing and reading a %s' % self.container_type
        identifier = 'TEST_%s' % self.container_type
        nwbfile = NWBFile(
            session_description=session_description,
            identifier=identifier,
            session_start_time=self.start_time,
            file_create_date=self.create_date
        )
        self.addContainer(nwbfile)

        with warnings.catch_warnings(record=True) as ws:
            with NWBHDF5IO(self.filename, mode='w') as write_io:
                write_io.write(nwbfile, cache_spec=cache_spec)

            self.validate()

            self.reader = NWBHDF5IO(self.filename, mode='r')
            self.read_nwbfile = self.reader.read()

        if ws:
            for w in ws:
                if issubclass(w.category, (MissingRequiredBuildWarning,
                                           BrokenLinkWarning)):
                    raise Exception('%s: %s' % (w.category.__name__, w.message))
                else:
                    warnings.showwarning(w.message, w.category, w.filename, w.lineno, w.file, w.line)

        try:
            return self.getContainer(self.read_nwbfile)
        except Exception as e:
            self.reader.close()
            self.reader = None
            raise e

    def roundtripExportContainer(self, cache_spec=True):
        """
        Add the test Container to an NWBFile, write it to file, read the file, export the read NWBFile to another
        file, and return the test Container from the file
        """
        self.roundtripContainer(cache_spec=cache_spec)  # self.read_nwbfile is now set

        with warnings.catch_warnings(record=True) as ws:
            NWBHDF5IO.export_io(
                src_io=self.reader,
                path=self.export_filename,
                cache_spec=cache_spec,
            )

            self.validate()

            self.export_reader = NWBHDF5IO(self.export_filename, mode='r')
            self.read_exported_nwbfile = self.export_reader.read()

        if ws:
            for w in ws:
                if issubclass(w.category, (MissingRequiredBuildWarning,
                                           BrokenLinkWarning)):
                    raise Exception('%s: %s' % (w.category.__name__, w.message))
                else:
                    warnings.showwarning(w.message, w.category, w.filename, w.lineno, w.file, w.line)

        try:
            return self.getContainer(self.read_exported_nwbfile)
        except Exception as e:
            self.export_reader.close()
            self.export_reader = None
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
        """ Validate the created files """
        if os.path.exists(self.filename):
            errors, _ = pynwb_validate(paths=[self.filename])
            if errors:
                raise Exception("\n".join(errors))

        if os.path.exists(self.export_filename):
            errors, _ = pynwb_validate(paths=[self.export_filename])
            if errors:
                raise Exception("\n".join(errors))


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


class NWBH5IOFlexMixin(metaclass=ABCMeta):
    """
    Mixin class that includes methods to run a flexible roundtrip test.
    The setUp, test_roundtrip, and tearDown methods will be run by unittest.

    The abstract methods getContainerType, addContainer, and getContainer must be
    implemented by classes that includethis mixin.

    Example::

        class TestMyContainerIO(NWBH5IOFlexMixin, TestCase):
            def getContainerType(self):
                # return the name of the type of Container being tested, for test ID purposes
            def addContainer(self):
                # add the test Container to the test NWB file
            def getContainer(self, nwbfile):
                # return the test Container from an NWB file

    This class is more flexible than NWBH5IOMixin and should be used for new roundtrip tests.

    This code is adapted from hdmf.testing.H5RoundTripMixin.
    """

    def setUp(self):
        container_type = self.getContainerType().replace(" ", "_")
        session_description = 'A file to test writing and reading a %s' % container_type
        identifier = 'TEST_%s' % container_type
        session_start_time = datetime(1971, 1, 1, 12, tzinfo=tzutc())
        self.nwbfile = NWBFile(
            session_description=session_description,
            identifier=identifier,
            session_start_time=session_start_time,
        )
        self.addContainer()
        self.container = self.getContainer(self.nwbfile)
        self.filename = 'test_%s.nwb' % container_type
        self.export_filename = 'test_export_%s.nwb' % container_type
        self.reader = None
        self.export_reader = None

    def tearDown(self):
        if self.reader is not None:
            self.reader.close()
        if self.export_reader is not None:
            self.export_reader.close()
        remove_test_file(self.filename)
        remove_test_file(self.export_filename)

    def get_manager(self):
        return get_manager()  # get the pynwb manager unless overridden

    @abstractmethod
    def getContainerType(self) -> str:
        """Return the name of the type of Container being tested, for test ID purposes."""
        raise NotImplementedError('Cannot run test unless getContainerType is implemented.')

    @abstractmethod
    def addContainer(self):
        """Add the test Container to the NWBFile.

        The NWBFile is accessible from self.nwbfile.
        The Container should be accessible from getContainer(self.nwbfile).
        """
        raise NotImplementedError('Cannot run test unless addContainer is implemented.')

    @abstractmethod
    def getContainer(self, nwbfile: NWBFile):
        """Return the test Container from the given NWBFile."""
        raise NotImplementedError('Cannot run test unless getContainer is implemented.')

    def test_roundtrip(self):
        """Test whether the read Container has the same contents as the original Container and validate the file.
        """
        self.read_container = self.roundtripContainer()
        self.assertIsNotNone(str(self.container))  # added as a test to make sure printing works
        self.assertIsNotNone(str(self.read_container))
        # make sure we get a completely new object
        self.assertNotEqual(id(self.container), id(self.read_container))
        # make sure the object ID is preserved
        self.assertIs(self.read_nwbfile.objects[self.container.object_id], self.read_container)
        self.assertContainerEqual(self.read_container, self.container)

    def test_roundtrip_export(self):
        """
        Test whether the test Container read from an exported file has the same contents as the original test Container
        and validate the file.
        """
        self.read_container = self.roundtripExportContainer()  # this container is read from the exported file
        self.assertIsNotNone(str(self.read_container))  # added as a test to make sure printing works
        # make sure we get a completely new object
        self.assertNotEqual(id(self.container), id(self.read_container))
        # make sure the object ID is preserved
        self.assertIs(self.read_exported_nwbfile.objects[self.container.object_id], self.read_container)
        self.assertContainerEqual(self.read_container, self.container, ignore_hdmf_attrs=True)

    def roundtripContainer(self, cache_spec=True):
        """Write the file, validate the file, read the file, and return the Container from the file.
        """

        # catch all warnings
        with warnings.catch_warnings(record=True) as ws:
            with NWBHDF5IO(self.filename, mode='w', manager=self.get_manager()) as write_io:
                write_io.write(self.nwbfile, cache_spec=cache_spec)

            self.validate()

            # this is not closed until tearDown() or an exception from self.getContainer below
            self.reader = NWBHDF5IO(self.filename, mode='r', manager=self.get_manager())
            self.read_nwbfile = self.reader.read()

        # parse warnings and raise exceptions for certain types of warnings
        if ws:
            for w in ws:
                if issubclass(w.category, (MissingRequiredBuildWarning,
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

    def roundtripExportContainer(self, cache_spec=True):
        """
        Roundtrip the container, then export the read NWBFile to a new file, validate the files, and return the test
        Container from the file.
        """
        # write and read the file. self.reader will be set
        self.roundtripContainer(cache_spec=cache_spec)

        # catch all warnings
        with warnings.catch_warnings(record=True) as ws:
            NWBHDF5IO.export_io(
                src_io=self.reader,
                path=self.export_filename,
                cache_spec=cache_spec,
            )

            self.validate()

            # this is not closed until tearDown() or an exception from self.getContainer below
            self.export_reader = NWBHDF5IO(self.export_filename, mode='r', manager=self.get_manager())
            self.read_exported_nwbfile = self.export_reader.read()

        # parse warnings and raise exceptions for certain types of warnings
        if ws:
            for w in ws:
                if issubclass(w.category, (MissingRequiredBuildWarning,
                                           BrokenLinkWarning)):
                    raise Exception('%s: %s' % (w.category.__name__, w.message))
                else:
                    warnings.warn(w.message, w.category)

        try:
            return self.getContainer(self.read_exported_nwbfile)
        except Exception as e:
            self.export_reader.close()
            self.export_reader = None
            raise e

    def validate(self):
        """Validate the created files."""
        if os.path.exists(self.filename):
            errors, _ = pynwb_validate(paths=[self.filename])
            if errors:
                raise Exception("\n".join(errors))

        if os.path.exists(self.export_filename):
            errors, _ = pynwb_validate(paths=[self.export_filename])
            if errors:
                raise Exception("\n".join(errors))
