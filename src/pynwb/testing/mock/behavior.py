import numpy as np

from ...behavior import (
    PupilTracking,
    Position,
    SpatialSeries,
    CompassDirection,
)
from .utils import name_generator
from .base import mock_TimeSeries


def mock_SpatialSeries(
    name=None,
    data=None,
    reference_frame="lower left is (0, 0)",
    unit="meters",
    conversion=1.0,
    resolution=-1.0,
    timestamps=None,
    starting_time=None,
    rate=10.0,
    comments="no comments",
    description="no description",
    control=None,
    control_description=None,
):
    return SpatialSeries(
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


def mock_Position(
    name=None, spatial_series=None,
):
    return Position(name=name or name_generator("Position"), spatial_series=spatial_series or [mock_SpatialSeries()])


def mock_PupilTracking(
    name=None, time_series=None,
):
    return PupilTracking(name=name or name_generator("PupilTracking"), time_series=time_series or [mock_TimeSeries()])


def mock_CompassDirection(name=None, spatial_series=None):
    return CompassDirection(
        name=name or name_generator("CompassDirection"),
        spatial_series=spatial_series or [mock_SpatialSeries(unit="radians")],
    )
