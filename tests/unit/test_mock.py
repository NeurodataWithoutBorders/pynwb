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

from pynwb.testing.mock.device import mock_Device

from pynwb.testing.mock.behavior import (
    mock_Position,
    mock_PupilTracking,
    mock_CompassDirection,
    mock_SpatialSeries,
)

from pynwb.testing.mock.ecephys import (
    mock_ElectrodeGroup,
    mock_ElectrodeTable,
    mock_ElectricalSeries,
    mock_SpikeEventSeries,
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


@pytest.mark.parametrize(
    "mock_function", [
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
        mock_Position,
        mock_PupilTracking,
        mock_CompassDirection,
        mock_SpatialSeries,
        mock_ElectrodeGroup,
        mock_ElectrodeTable,
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
    ],
)
def test_mock(mock_function):
    mock_function()


def test_name_generator():

    name_generator_registry.clear()  # reset registry

    assert name_generator("TimeSeries") == "TimeSeries"
    assert name_generator("TimeSeries") == "TimeSeries2"
