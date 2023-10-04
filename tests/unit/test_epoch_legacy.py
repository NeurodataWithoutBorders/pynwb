from pynwb.epoch import TimeIntervals
from pynwb.testing import NWBH5IOMixin, TestCase
from pynwb import NWBFile, NWBHDF5IO
from pynwb.base import TimeSeries, TimeSeriesReference, TimeSeriesReferenceVectorData
import numpy as np
import h5py


class TestTimeIntervalsIO(NWBH5IOMixin, TestCase):
    """
    Test that reading NWB files with version 2.4 and earlier function correctly with the TimeIntervals type.
    In NWB 2.5 TimeIntervals.timeseries was updated to use the TimeSeriesReferenceVectorData type and to
    keep the API consistent old files are migrated on read to present the same API for those files. This
    is possible because the previous and updated schema are identical aside from the fact that a dedicated
    neurodata_type was created for the TimeIntervals.timeseries columns which is also used in the
    IntracellularRecordingTable type.

    This is technically a round-trip test, but without round-trip we can't test the object-mapper and
    including it here makes sure this gets included in code-coverage tests as well.
    """

    def setUpContainer(self):
        """ Return placeholder epochs object. Tested epochs are added directly to the NWBFile in addContainer """
        return TimeIntervals('epochs')

    def addContainer(self, nwbfile):
        """ Add the test epochs to the given NWBFile """
        # Add some timeseries
        tsa, tsb = [
            TimeSeries(name='a', data=np.arange(11), unit='flubs', timestamps=np.linspace(0, 1.0, 11)),
            TimeSeries(name='b', data=np.arange(13), unit='flubs', timestamps=np.linspace(0.1, 2.0, 13)),
        ]
        nwbfile.add_acquisition(tsa)
        nwbfile.add_acquisition(tsb)
        # Add a custom column
        nwbfile.add_epoch_column(
            name='temperature',
            description='average temperature (c) during epoch'
        )
        # Add some epochs
        nwbfile.add_epoch(
            start_time=0.0,
            stop_time=0.5,
            timeseries=[tsa, tsb],
            tags='ambient',
            temperature=26.4,
        )
        nwbfile.add_epoch(
            start_time=1.3,
            stop_time=4.1,
            timeseries=[tsa, ],
            tags='ambient',
            temperature=26.4,
        )
        # reset the thing
        self.container = nwbfile.epochs

    def getContainer(self, nwbfile):
        """ Return the test epochs from the given NWBFile """
        return nwbfile.epochs

    def test_legacy_format(self):
        description = 'a file to test writing and reading a %s' % self.container_type
        identifier = 'TEST_%s' % self.container_type
        nwbfile = NWBFile(description, identifier, self.start_time, file_create_date=self.create_date)
        self.addContainer(nwbfile)

        # write the file
        with NWBHDF5IO(self.filename, mode='w') as write_io:
            write_io.write(nwbfile, cache_spec=False)
        # Modify the HDF5 file to look like NWB 2.4 and earlier. This simply means
        # modifying the neurodata_type on the TimeIntervals.timeseries column
        with h5py.File(self.filename, mode='a') as infile:
            infile['/intervals/epochs/timeseries'].attrs['neurodata_type'] = 'VectorData'
            infile.attrs['nwb_version'] = '2.3.0'

        # Read the file back
        self.reader = NWBHDF5IO(self.filename, mode='r')
        self.read_nwbfile = self.reader.read()

        # Test that the VectorData column for timeseries has been converted to TimeSeriesReferenceVectorData
        self.assertIsInstance(self.read_nwbfile.epochs.timeseries, TimeSeriesReferenceVectorData)

        # Test that slicing into epochs.timeseries works as expected
        re = self.read_nwbfile.epochs.timeseries[0]
        self.assertIsInstance(re, TimeSeriesReference)
        self.assertTupleEqual((re[0], re[1], re[2].object_id), (0, 5, nwbfile.get_acquisition('a').object_id))

        # Test that slicing into epochs works as expected
        re = self.read_nwbfile.epochs[0:1]
        self.assertListEqual(re.columns.tolist(), ['start_time', 'stop_time', 'temperature', 'tags', 'timeseries'])
        for i in re.loc[0, 'timeseries']:
            self.assertIsInstance(i, TimeSeriesReference)
        self.assertTupleEqual(
            (re.loc[0, 'timeseries'][0][0], re.loc[0, 'timeseries'][0][1], re.loc[0, 'timeseries'][0][2].object_id),
            (0, 5, nwbfile.get_acquisition('a').object_id))
        self.assertTupleEqual(
            (re.loc[0, 'timeseries'][1][0], re.loc[0, 'timeseries'][1][1], re.loc[0, 'timeseries'][1][2].object_id),
            (0, 3, nwbfile.get_acquisition('b').object_id))
