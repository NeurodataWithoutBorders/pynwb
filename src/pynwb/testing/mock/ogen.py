import numpy as np

from ...ogen import OptogeneticStimulusSite, OptogeneticSeries

from .device import mock_Device
from .utils import name_generator


def mock_OptogeneticStimulusSite(
    name=None,
    device=None,
    description="optogenetic stimulus site",
    excitation_lambda=500.,
    location="part of the brain",
):
    return OptogeneticStimulusSite(
        name=name or name_generator("OptogeneticStimulusSite"),
        device=device or mock_Device(),
        description=description,
        excitation_lambda=excitation_lambda,
        location=location
    )


def mock_OptogeneticSeries(
    name=None,
    data=None,
    site=None,
    resolution=-1.0,
    conversion=1.0,
    timestamps=None,
    starting_time=None,
    rate=10.0,
    comments="no comments",
    description="no description",
    control=None,
    control_description=None,
):
    return OptogeneticSeries(
        name=name or name_generator("OptogeneticSeries"),
        data=data if data is not None else np.array([1, 2, 3, 4]),
        site=site or mock_OptogeneticStimulusSite(),
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
