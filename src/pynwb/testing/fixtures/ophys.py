import pytest

import numpy as np

from ...ophys import (
    TwoPhotonSeries,
    RoiResponseSeries,
    DfOverF,
    Fluorescence,
    PlaneSegmentation,
    ImageSegmentation,
    OpticalChannel,
    ImagingPlane,
    MotionCorrection,
    CorrectedImageStack
)

from ...image import ImageSeries

from .device import device


@pytest.fixture()
def optical_channel():
    return OpticalChannel(
        name='test_optical_channel',
        description='description',
        emission_lambda=500.
    )


@pytest.fixture()
def imaging_plane(optical_channel, device):

    return ImagingPlane(
        name='test_imaging_plane',
        optical_channel=optical_channel,
        description='description',
        device=device,
        excitation_lambda=600.,
        imaging_rate=300.,
        indicator='indicator',
        location='location',
        reference_frame='reference_frame',
        origin_coords=[10, 20],
        origin_coords_unit='oc_unit',
        grid_spacing=[1, 2, 3],
        grid_spacing_unit='gs_unit'
    )


@pytest.fixture()
def plane_segmentation(imaging_plane):
    w, h = 5, 5
    img_mask = [[[1.0 for x in range(w)] for y in range(h)], [[2.0 for x in range(w)] for y in range(h)]]
    pix_mask = [[1, 2, 1.0], [3, 4, 1.0], [5, 6, 1.0],
                [7, 8, 2.0], [9, 10, 2.0]]

    iSS = ImageSeries(
        name='test_iS',
        data=np.ones((2, 2, 2)),
        unit='unit',
        external_file=['external_file'],
        starting_frame=[1, 2, 3],
        format='tiff',
        timestamps=[1., 2.]
    )

    pS = PlaneSegmentation(
        description='description',
        imaging_plane=imaging_plane,
        name='test_name',
        reference_images=iSS
    )
    pS.add_roi(pixel_mask=pix_mask[0:3], image_mask=img_mask[0])
    pS.add_roi(pixel_mask=pix_mask[3:5], image_mask=img_mask[1])
    return pS

