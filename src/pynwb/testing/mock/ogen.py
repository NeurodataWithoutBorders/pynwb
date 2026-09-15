from typing import Optional

import numpy as np

from ... import NWBFile
from ...device import Device
from ...ogen import OptogeneticStimulusSite, OptogeneticSeries

from .device import mock_Device
from .utils import name_generator


def mock_OptogeneticStimulusSite(
    name: Optional[str] = None,
    device: Optional[Device] = None,
    description: str = "optogenetic stimulus site",
    excitation_lambda: float = 500.,
    location: str = "part of the brain",
    nwbfile: Optional[NWBFile] = None,
) -> OptogeneticStimulusSite:
    optogenetic_stimulus_site = OptogeneticStimulusSite(
        name=name or name_generator("OptogeneticStimulusSite"),
        device=device or mock_Device(nwbfile=nwbfile),
        description=description,
        excitation_lambda=excitation_lambda,
        location=location
    )

    if nwbfile is not None:
        nwbfile.add_ogen_site(optogenetic_stimulus_site)

    return optogenetic_stimulus_site


def mock_OptogeneticSeries(
    name: Optional[str] = None,
    data=None,
    site: Optional[OptogeneticStimulusSite] = None,
    resolution: float = -1.0,
    conversion: float = 1.0,
    timestamps=None,
    starting_time: Optional[float] = None,
    rate: Optional[float] = 10.0,
    comments: str = "no comments",
    description: str = "no description",
    control=None,
    control_description=None,
    nwbfile: Optional[NWBFile] = None,
) -> OptogeneticSeries:
    optogenetic_series = OptogeneticSeries(
        name=name or name_generator("OptogeneticSeries"),
        data=data if data is not None else np.array([1, 2, 3, 4]),
        site=site or mock_OptogeneticStimulusSite(nwbfile=nwbfile),
        resolution=resolution,
        conversion=conversion,
        timestamps=timestamps,
        starting_time=starting_time,
        rate=rate,
        comments=comments,
        description=description,
        control=control,
        control_description=control_description,
    )

    if nwbfile is not None:
        nwbfile.add_acquisition(optogenetic_series)

    return optogenetic_series
