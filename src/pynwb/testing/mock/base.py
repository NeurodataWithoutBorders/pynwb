from typing import Optional

import numpy as np

from ... import NWBFile
from ...base import TimeSeries
from .utils import name_generator


def mock_TimeSeries(
    name: Optional[str] = None,
    data=None,
    unit: str = "volts",
    resolution: float = -1.0,
    conversion: float = 1.0,
    timestamps=None,
    starting_time: Optional[float] = None,
    rate: Optional[float] = 10.0,
    comments: str = "no comments",
    description: str = "no description",
    control=None,
    control_description=None,
    continuity=None,
    nwbfile: Optional[NWBFile] = None,
) -> TimeSeries:
    time_series = TimeSeries(
        name=name or name_generator("TimeSeries"),
        data=data if data is not None else np.array([1, 2, 3, 4]),
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

    if nwbfile is not None:
        nwbfile.add_acquisition(time_series)

    return time_series
