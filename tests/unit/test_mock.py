import numpy as np

from pynwb import NWBHDF5IO

from pynwb.testing.mock.file import mock_Subject, mock_NWBFile

from pynwb.testing.mock.base import mock_TimeSeries

from pynwb.testing.mock.ophys import (
    mock_ImagingPlane,
    mock_OnePhotonSeries,
    mock_TwoPhotonSeries,
    mock_RoiResponseSeries,
    mock_PlaneSegmentation,
    mock_OpticalChannel,
    mock_Fluorescence,
    mock_DfOverF,
    mock_ImageSegmentation,
)

from pynwb.testing.mock.ogen import (
    mock_OptogeneticStimulusSite,
    mock_OptogeneticSeries
)

from pynwb.testing.mock.device import mock_Device, mock_DeviceModel

from pynwb.testing.mock.behavior import (
    mock_Position,
    mock_PupilTracking,
    mock_CompassDirection,
    mock_SpatialSeries,
)

from pynwb.testing.mock.ecephys import (
    mock_ElectrodeGroup,
    mock_ElectrodesTable,
    mock_electrodes,
    mock_ElectricalSeries,
    mock_SpikeEventSeries,
    mock_Units,
)

from pynwb.testing.mock.icephys import (
    mock_IntracellularElectrode,
    mock_CurrentClampSeries,
    mock_IZeroClampSeries,
    mock_VoltageClampSeries,
    mock_VoltageClampStimulusSeries,
    mock_CurrentClampStimulusSeries,
    mock_IntracellularRecordingsTable,
)

import pytest

from pynwb.testing.mock.utils import name_generator, name_generator_registry

mock_functions = [
    mock_ImagingPlane,
    mock_OnePhotonSeries,
    mock_TwoPhotonSeries,
    mock_RoiResponseSeries,
    mock_PlaneSegmentation,
    mock_OpticalChannel,
    mock_Fluorescence,
    mock_DfOverF,
    mock_ImageSegmentation,
    mock_OptogeneticStimulusSite,
    mock_OptogeneticSeries,
    mock_Device,
    mock_DeviceModel,
    mock_Position,
    mock_PupilTracking,
    mock_CompassDirection,
    mock_SpatialSeries,
    mock_ElectrodeGroup,
    mock_ElectrodesTable,
    mock_ElectricalSeries,
    mock_SpikeEventSeries,
    mock_Subject,
    mock_NWBFile,
    mock_TimeSeries,
    mock_CurrentClampSeries,
    mock_IZeroClampSeries,
    mock_VoltageClampSeries,
    mock_VoltageClampStimulusSeries,
    mock_IntracellularElectrode,
    mock_CurrentClampStimulusSeries,
    mock_IntracellularRecordingsTable,
    mock_Units,
]


@pytest.mark.parametrize("mock_function", mock_functions)
def test_mock(mock_function):
    mock_function()


def test_mock_TimeSeries_w_timestamps():
    ts = mock_TimeSeries(timestamps=[0, 1, 2, 3])
    assert ts.timestamps is not None
    assert len(ts.timestamps) == 4


def test_mock_TimeSeries_w_no_time():
    ts = mock_TimeSeries()
    assert ts.rate == 10.0


def test_mock_electrodes_sizes_table_to_n_electrodes():
    """The auto-created table must have exactly n_electrodes rows so the region of n_electrodes is in range."""
    region = mock_electrodes(n_electrodes=128)
    assert len(region.data) == 128
    assert len(region.table) == 128


def test_mock_ElectricalSeries_more_than_five_channels():
    """mock_ElectricalSeries must support data with more than the default 5 channels."""
    electrical_series = mock_ElectricalSeries(data=np.ones((10, 128)))
    assert electrical_series.data.shape[1] == 128
    assert len(electrical_series.electrodes.table) == 128


def test_mock_Device_links_model():
    """mock_Device must link the given DeviceModel and set the serial number."""
    model = mock_DeviceModel()
    device = mock_Device(model=model, serial_number="1234")
    assert device.model is model
    assert device.serial_number == "1234"


def test_mock_Device_adds_model_to_nwbfile():
    """A linked DeviceModel must be placed in the NWBFile so that the link resolves."""
    nwbfile = mock_NWBFile()
    model = mock_DeviceModel()
    device = mock_Device(model=model, nwbfile=nwbfile)
    assert nwbfile.device_models[model.name] is model
    assert nwbfile.devices[device.name] is device


def test_mock_Device_model_already_in_nwbfile():
    """A DeviceModel already in the NWBFile must be linked without being added a second time."""
    nwbfile = mock_NWBFile()
    model = mock_DeviceModel(nwbfile=nwbfile)
    device = mock_Device(model=model, nwbfile=nwbfile)
    assert device.model is model
    assert len(nwbfile.device_models) == 1


def test_mock_Device_model_name_clash():
    """A DeviceModel whose name is taken by a different DeviceModel in the NWBFile must raise."""
    nwbfile = mock_NWBFile()
    mock_DeviceModel(name="clashing_name", nwbfile=nwbfile)
    other_model = mock_DeviceModel(name="clashing_name")

    with pytest.raises(ValueError, match="already exists in 'device_models'"):
        mock_Device(model=other_model, nwbfile=nwbfile)


def test_mock_Device_with_model_roundtrip(tmp_path):
    """The link from a written Device to its DeviceModel must resolve on read."""
    nwbfile = mock_NWBFile()
    model = mock_DeviceModel()
    device = mock_Device(model=model, serial_number="1234", nwbfile=nwbfile)

    path = tmp_path / "device_with_model.nwb"
    with NWBHDF5IO(path, "w") as io:
        io.write(nwbfile)

    with NWBHDF5IO(path, "r") as io:
        read_nwbfile = io.read()
        read_device = read_nwbfile.devices[device.name]
        assert read_device.model is read_nwbfile.device_models[model.name]
        assert read_device.serial_number == "1234"


@pytest.mark.parametrize("mock_function", mock_functions)
def test_mock_write(mock_function, tmp_path):
    if mock_function is mock_NWBFile:
        return
    nwbfile = mock_NWBFile()
    assert mock_function(nwbfile=nwbfile) is not None

    test_file = tmp_path / (mock_function.__name__ + ".nwb")
    with NWBHDF5IO(test_file, "w") as io:
        io.write(nwbfile)


def test_name_generator():
    name_generator_registry.clear()  # reset registry
    assert name_generator("TimeSeries") == "TimeSeries"
    assert name_generator("TimeSeries") == "TimeSeries2"


@pytest.mark.parametrize("mask_type", ["image_mask", "pixel_mask", "voxel_mask"])
def test_mock_PlaneSegmentation_mask_type(mask_type):
    plane_segmentation = mock_PlaneSegmentation(mask_type=mask_type)
    assert getattr(plane_segmentation, mask_type) is not None

