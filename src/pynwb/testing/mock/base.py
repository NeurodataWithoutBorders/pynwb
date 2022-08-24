import numpy as np

from ...base import TimeSeries
from .utils import name_generator


def mock_TimeSeries(
    name=name_generator("TimeSeries"),
    data=np.array([1, 2, 3, 4]),
    unit="volts",
    resolution=-1.0,
    conversion=1.0,
    timestamps=None,
    starting_time=None,
    rate=10.0,
    comments="no comments",
    description="no description",
    control=None,
    control_description=None,
    continuity=None,
):
    return TimeSeries(
        name=name,
        data=data,
        unit=unit,
        resolution=resolution,
        conversion=conversion,
        timestamps=timestamps,
        starting_time=starting_time,
        rate=rate,
        comments=comments,
        description=description,
        control=control,
        control_description=control_description,
        continuity=continuity,
    )
