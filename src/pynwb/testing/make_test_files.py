import numpy as np

from datetime import datetime
from pynwb import NWBFile, NWBHDF5IO, __version__, TimeSeries
from pynwb.image import ImageSeries

# pynwb 1.0.2 should be installed with hdmf 1.0.3
# pynwb 1.0.3 should be installed with hdmf 1.0.5
# pynwb 1.1.0 should be installed with hdmf 1.2.0
# pynwb 1.1.1+ should be installed with an appropriate version of hdmf


def _write(test_name, nwbfile):
    filename = 'tests/back_compat/%s_%s.nwb' % (__version__, test_name)

    with NWBHDF5IO(filename, 'w') as io:
        io.write(nwbfile)

    return filename


def make_nwbfile_empty():
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    test_name = 'nwbfile'
    _write(test_name, nwbfile)


def make_nwbfile_str_experimenter():
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone(),
                      experimenter='one experimenter')
    test_name = 'str_experimenter'
    _write(test_name, nwbfile)


def make_nwbfile_str_pub():
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone(),
                      related_publications='one publication')
    test_name = 'str_pub'
    _write(test_name, nwbfile)


def make_nwbfile_timeseries_no_data():
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    ts = TimeSeries(
        name='test_timeseries',
        rate=1.,
        unit='unit',
    )
    nwbfile.add_acquisition(ts)

    test_name = 'timeseries_no_data'
    _write(test_name, nwbfile)


def make_nwbfile_timeseries_no_unit():
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    ts = TimeSeries(
        name='test_timeseries',
        data=[0],
        rate=1.,
    )
    nwbfile.add_acquisition(ts)

    test_name = 'timeseries_no_unit'
    _write(test_name, nwbfile)


def make_nwbfile_imageseries_no_data():
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    image_series = ImageSeries(
        name='test_imageseries',
        external_file=['external_file'],
        starting_frame=[1, 2, 3],
        format='tiff',
        timestamps=[1., 2., 3.]
    )

    nwbfile.add_acquisition(image_series)

    test_name = 'imageseries_no_data'
    _write(test_name, nwbfile)


def make_nwbfile_imageseries_no_unit():
    """Create a test file with an ImageSeries with data and no unit."""
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    image_series = ImageSeries(
        name='test_imageseries',
        data=np.ones((3, 3, 3)),
        external_file=['external_file'],
        starting_frame=[1, 2, 3],
        format='tiff',
        timestamps=[1., 2., 3.]
    )

    nwbfile.add_acquisition(image_series)

    test_name = 'imageseries_no_unit'
    _write(test_name, nwbfile)


if __name__ == '__main__':

    if __version__ == '1.1.2':
        make_nwbfile_empty()
        make_nwbfile_str_experimenter()
        make_nwbfile_str_pub()

    if __version__ == '1.5.1':
        make_nwbfile_timeseries_no_data()
        make_nwbfile_timeseries_no_unit()
        make_nwbfile_imageseries_no_data()
        make_nwbfile_imageseries_no_unit()
