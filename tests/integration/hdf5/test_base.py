import numpy as np
from datetime import datetime
from dateutil.tz import tzlocal

from pynwb import TimeSeries, NWBFile, NWBHDF5IO
from pynwb.base import Images, Image, ImageReferences
from pynwb.testing import AcquisitionH5IOMixin, TestCase, remove_test_file


class TestTimeSeriesIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test TimeSeries to read/write """
        return TimeSeries(
            name='test_timeseries',
            data=list(range(1000)),
            unit='SIunit',
            timestamps=np.arange(1000.),
            resolution=0.1,
            continuity='continuous',
        )


class TestTimeSeriesLinking(TestCase):

    def setUp(self):
        self.path = 'test_timestamps_linking.nwb'

    def tearDown(self):
        remove_test_file(self.path)

    def test_timestamps_linking(self):
        ''' Test that timestamps get linked to in TimeSeries '''
        tsa = TimeSeries(name='a', data=np.linspace(0, 1, 1000), timestamps=np.arange(1000.), unit='m')
        tsb = TimeSeries(name='b', data=np.linspace(0, 1, 1000), timestamps=tsa, unit='m')
        nwbfile = NWBFile(identifier='foo',
                          session_start_time=datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzlocal()),
                          session_description='bar')
        nwbfile.add_acquisition(tsa)
        nwbfile.add_acquisition(tsb)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)
        with NWBHDF5IO(self.path, 'r') as io:
            nwbfile = io.read()
        tsa = nwbfile.acquisition['a']
        tsb = nwbfile.acquisition['b']
        self.assertIs(tsa.timestamps, tsb.timestamps)

    def test_data_linking(self):
        ''' Test that data get linked to in TimeSeries '''
        tsa = TimeSeries(name='a', data=np.linspace(0, 1, 1000), timestamps=np.arange(1000.), unit='m')
        tsb = TimeSeries(name='b', data=tsa, timestamps=np.arange(1000.), unit='m')
        tsc = TimeSeries(name='c', data=tsb, timestamps=np.arange(1000.), unit='m')
        nwbfile = NWBFile(identifier='foo',
                          session_start_time=datetime(2017, 5, 1, 12, 0, 0, tzinfo=tzlocal()),
                          session_description='bar')
        nwbfile.add_acquisition(tsa)
        nwbfile.add_acquisition(tsb)
        nwbfile.add_acquisition(tsc)
        with NWBHDF5IO(self.path, 'w') as io:
            io.write(nwbfile)
        with NWBHDF5IO(self.path, 'r') as io:
            nwbfile = io.read()
        tsa = nwbfile.acquisition['a']
        tsb = nwbfile.acquisition['b']
        tsc = nwbfile.acquisition['c']
        self.assertIs(tsa.data, tsb.data)
        self.assertIs(tsa.data, tsc.data)


class TestImagesIO(AcquisitionH5IOMixin, TestCase):

    def setUpContainer(self):
        """ Return the test Images to read/write """
        image1 = Image(name='test_image', data=np.ones((10, 10)))
        image2 = Image(name='test_image2', data=np.ones((10, 10)))
        image_references = ImageReferences(name='order_of_images', data=[image2, image1])
        images = Images(name='images_name', images=[image1, image2], order_of_images=image_references)

        return images
