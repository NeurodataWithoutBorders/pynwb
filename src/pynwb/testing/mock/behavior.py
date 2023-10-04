from typing import Optional

import numpy as np

from ... import NWBFile, TimeSeries
from ...behavior import (
    PupilTracking,
    Position,
    SpatialSeries,
    CompassDirection,
)
from .utils import name_generator
from .base import mock_TimeSeries


def mock_SpatialSeries(
    name: Optional[str] = None,
    data=None,
    reference_frame: str = "lower left is (0, 0)",
    unit: str = "meters",
    conversion=1.0,
    resolution=-1.0,
    timestamps=None,
    starting_time: Optional[float] = None,
    rate: Optional[float] = 10.0,
    comments: str = "no comments",
    description: str = "no description",
    control=None,
    control_description=None,
    nwbfile: Optional[NWBFile] = None,
) -> SpatialSeries:
    spatial_series = SpatialSeries(
        name=name or name_generator("SpatialSeries"),
        data=data if data is not None else np.array([1, 2, 3, 4]),
        reference_frame=reference_frame,
        unit=unit,
        conversion=conversion,
        resolution=resolution,
        timestamps=timestamps,
        starting_time=starting_time,
        rate=rate,
        comments=comments,
        description=description,
        control=control,
        control_description=control_description,
    )

    if nwbfile is not None:
        nwbfile.add_acquisition(spatial_series)

    return spatial_series


def mock_Position(
        name: Optional[str] = None, spatial_series: Optional[SpatialSeries] = None, nwbfile: Optional[NWBFile] = None,
) -> Position:

    position = Position(
        name=name or name_generator("Position"), spatial_series=spatial_series or [mock_SpatialSeries(nwbfile=nwbfile)]
    )

    if nwbfile is not None:
        nwbfile.add_acquisition(position)
    return position


def mock_PupilTracking(
    name: Optional[str] = None, time_series: Optional[TimeSeries] = None, nwbfile: Optional[NWBFile] = None
) -> PupilTracking:
    pupil_tracking = PupilTracking(
        name=name or name_generator("PupilTracking"), time_series=time_series or [mock_TimeSeries(nwbfile=nwbfile)]
    )

    if nwbfile is not None:
        nwbfile.add_acquisition(pupil_tracking)

    return pupil_tracking


def mock_CompassDirection(
        name: Optional[str] = None, spatial_series: Optional[SpatialSeries] = None, nwbfile: Optional[NWBFile] = None
) -> CompassDirection:

    compass_direction = CompassDirection(
        name=name or name_generator("CompassDirection"),
        spatial_series=spatial_series or [mock_SpatialSeries(unit="radians", nwbfile=nwbfile)],
    )

    if nwbfile is not None:
        nwbfile.add_acquisition(compass_direction)

    return compass_direction
