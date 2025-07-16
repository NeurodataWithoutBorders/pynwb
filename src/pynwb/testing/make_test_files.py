from datetime import datetime
import numpy as np
from pathlib import Path
from pynwb import NWBFile, NWBHDF5IO, __version__, TimeSeries, get_class, load_namespaces
from pynwb.ecephys import ElectricalSeries
from pynwb.file import Subject
from pynwb.image import ImageSeries
from pynwb.misc import DecompositionSeries
from pynwb.spec import NWBNamespaceBuilder, export_spec, NWBGroupSpec, NWBAttributeSpec


# pynwb 1.0.2 should be installed with hdmf 1.0.3
# pynwb 1.0.3 should be installed with hdmf 1.0.5
# pynwb 1.1.0 should be installed with hdmf 1.2.0
# pynwb 1.1.1+ should be installed with an appropriate version of hdmf


def _write(test_name, nwbfile):
    filename = str("%s/%s_%s.nwb") % (Path(__file__).parent, __version__, test_name)
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


def _make_empty_with_extension():
    ns_builder = NWBNamespaceBuilder(
        doc="An NWB test extension",
        name="ndx-testextension",
        version="0.1.0",
        author="PyNWB Test File Generator",
        contact="my_email@example.com",
    )

    ns_builder.include_type('TimeSeries', namespace='core')
    tetrode_series = NWBGroupSpec(
        neurodata_type_def='TimeSeriesWithID',
        neurodata_type_inc='TimeSeries',
        doc=('An extension of TimeSeries to include an ID.'),
        attributes=[
            NWBAttributeSpec(
                name='id',
                doc='The time series ID.',
                dtype='int32'
            ),
        ],
    )

    new_data_types = [tetrode_series]

    # export the spec to yaml files in the current directory
    export_spec(ns_builder, new_data_types, output_dir=".")

    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())

    load_namespaces("ndx-testextension.namespace.yaml")  # load from the current directory
    TimeSeriesWithID = get_class("TimeSeriesWithID", "ndx-testextension")
    ts = TimeSeriesWithID(
        name="test_ts",
        data=[1., 2., 3.],
        description="ADDME",
        unit="ADDME",
        rate=1.,
        id=1,
    )
    nwbfile.add_acquisition(ts)
    test_name = 'nwbfile_with_extension'
    _write(test_name, nwbfile)


def _make_subject_without_age_reference():
    """Create a test file without a value for age_reference."""
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    subject = Subject(
        age="P90D",
        description="A rat",
        subject_id="RAT123",
    )

    nwbfile.subject = subject

    test_name = 'subject_no_age__reference'
    _write(test_name, nwbfile)

def _make_electrodes_dynamic_table():
    """Create a test file where electrodes is a dynamic table and not its own type."""
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    device = nwbfile.create_device(name="array", description="an array")
    nwbfile.add_electrode_column(name="label", description="label of electrode")

    for i in range(4):
        electrode_group = nwbfile.create_electrode_group(
            name=f"shank{i}",
            description=f"electrode group for shank {i}",
            device=device,
            location="brain area",
        )
        for j in range(3):
            nwbfile.add_electrode(
                group=electrode_group,
                location="brain area",
                label=f"shank{i}electrode{j}",
            )

    nwbfile.add_unit(
        spike_times=[0.1, 0.2, 0.3],
        electrodes=[0, 1],
    )

    eseries = ElectricalSeries(
        name="ElectricalSeries",
        description="Test electrodes reference",
        data=[[0.1, 0.2], [0.3, 0.4], [0.5, 0.6]],
        timestamps=[0.1, 0.2, 0.3],
        electrodes=nwbfile.create_electrode_table_region(region=[2, 3], description="electrodes table indices 2 and 3"),
    )
    nwbfile.add_acquisition(eseries)

    test_name = 'electrodes_dynamic_table'
    _write(test_name, nwbfile)

def _make_bands_dynamic_table():
    """Create a test file where electrodes is a dynamic table and not its own type."""
    nwbfile = NWBFile(session_description='ADDME',
                      identifier='ADDME',
                      session_start_time=datetime.now().astimezone())
    mod = nwbfile.create_processing_module(name="test_mod", description="a test module")
    ts = TimeSeries(
        name='dummy timeseries',
        description='desc',
        data=np.ones((3, 3)),
        unit='Volts',
        timestamps=np.ones((3,))
    )
    ds = DecompositionSeries(
        name='LFPSpectralAnalysis',
        description='my description',
        data=np.ones((3, 3, 3)),
        timestamps=[1., 2., 3.],
        source_timeseries=ts,
        metric='amplitude'
    )
    for band_name in ['alpha', 'beta', 'gamma']:
        ds.add_band(band_name=band_name, band_limits=np.array([1., 1.]), band_mean=1., band_stdev=1.)
    mod.add(ts)
    mod.add(ds)

    test_name = 'decompositionseries_bands_dynamic_table'
    _write(test_name, nwbfile)

if __name__ == '__main__':
    # install these versions of PyNWB and run this script to generate new files
    # python src/pynwb/testing/make_test_files.py
    # files will be made in src/pynwb/testing/
    # files should be moved to tests/back_compat/

    # NOTE: this script is run in the GitHub Actions workflow generate_test_files.yml

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
        _make_empty_with_extension()

    if __version__ == "2.2.0":
        _make_subject_without_age_reference()

    if __version__ == "3.0.0":
        _make_electrodes_dynamic_table()
        _make_bands_dynamic_table()