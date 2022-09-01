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


def _make_empty():
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    test_name = 'nwbfile'
    _write(test_name, nwbfile)


def _make_str_experimenter():
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone(),
                      experimenter='one experimenter')
    test_name = 'str_experimenter'
    _write(test_name, nwbfile)


def _make_str_pub():
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone(),
                      related_publications='one publication')
    test_name = 'str_pub'
    _write(test_name, nwbfile)


def _make_timeseries_no_data():
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


def _make_timeseries_no_unit():
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


def _make_imageseries_no_data():
    """Create a test file with an ImageSeries with no data."""
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    image_series = ImageSeries(
        name='test_imageseries',
        external_file=['external_file'],
        starting_frame=[1],
        format='external',
        timestamps=[1., 2., 3.]
    )

    nwbfile.add_acquisition(image_series)

    test_name = 'imageseries_no_data'
    _write(test_name, nwbfile)


def _make_imageseries_no_unit():
    """Create a test file with an ImageSeries with data and no unit."""
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    image_series = ImageSeries(
        name='test_imageseries',
        data=np.ones((3, 3, 3)),
        timestamps=[1., 2., 3.]
    )

    nwbfile.add_acquisition(image_series)

    test_name = 'imageseries_no_unit'
    _write(test_name, nwbfile)


def _make_imageseries_non_external_format():
    """Create a test file with an ImageSeries with external_file set and format != 'external'."""
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    image_series = ImageSeries(
        name='test_imageseries',
        external_file=['external_file'],
        starting_frame=[1],
        format='tiff',
        timestamps=[1., 2., 3.]
    )

    nwbfile.add_acquisition(image_series)

    test_name = 'imageseries_non_external_format'
    _write(test_name, nwbfile)


def _make_imageseries_nonmatch_starting_frame():
    """Create a test file with an ImageSeries where len(starting_frame) != len(external_file)."""
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    image_series = ImageSeries(
        name='test_imageseries',
        external_file=['external_file'],
        starting_frame=[1, 2, 3],
        format='external',
        timestamps=[1., 2., 3.]
    )

    nwbfile.add_acquisition(image_series)

    test_name = 'imageseries_nonmatch_starting_frame'
    _write(test_name, nwbfile)


if __name__ == '__main__':
    # install these versions of PyNWB and run this script to generate new files
    # python src/pynwb/testing/make_test_files.py

    if __version__ == '1.1.2':
        _make_empty()
        _make_str_experimenter()
        _make_str_pub()

    if __version__ == '1.5.1':
        _make_timeseries_no_data()
        _make_timeseries_no_unit()
        _make_imageseries_no_data()
        _make_imageseries_no_unit()

    if __version__ == '2.1.0':
        _make_imageseries_no_data()
        _make_imageseries_non_external_format()
        _make_imageseries_nonmatch_starting_frame()
