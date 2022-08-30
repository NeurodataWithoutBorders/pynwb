from pynwb.testing.mock.ophys import (
    mock_ImagingPlane,
    mock_TwoPhotonSeries,
    mock_RoiResponseSeries,
    mock_PlaneSegmentation,
    mock_OpticalChannel,
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

import pytest


@pytest.mark.parametrize(
    "mock_function", [
        mock_ImagingPlane,
        mock_TwoPhotonSeries,
        mock_RoiResponseSeries,
        mock_PlaneSegmentation,
        mock_OpticalChannel,
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
    ],
)
def test_mock(mock_function):
    mock_function()
