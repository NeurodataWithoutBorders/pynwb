import numpy as np

from hdmf.common.table import DynamicTableRegion
from ...ophys import (
    RoiResponseSeries,
    OpticalChannel,
    ImagingPlane,
    TwoPhotonSeries,
    PlaneSegmentation,
    ImageSegmentation,
    DfOverF,
    Fluorescence,
)
from .device import mock_Device
from .utils import name_generator


def mock_OpticalChannel(
    name=None,
    description="description",
    emission_lambda=500.0,
):
    return OpticalChannel(
        name=name or name_generator("OpticalChannel"), description=description, emission_lambda=emission_lambda,
    )


def mock_ImagingPlane(
    name=None,
    optical_channel=None,
    description="description",
    device=None,
    excitation_lambda=500.0,
    indicator="indicator",
    location="unknown",
    imaging_rate=30.0,
    manifold=None,
    conversion=1.0,
    unit="meters",
    reference_frame=None,
    origin_coords=None,
    origin_coords_unit="meters",
    grid_spacing=None,
    grid_spacing_unit="meters",
):
    return ImagingPlane(
        name=name or name_generator("ImagingPlane"),
        optical_channel=optical_channel or mock_OpticalChannel(),
        description=description,
        device=device or mock_Device(),
        excitation_lambda=excitation_lambda,
        indicator=indicator,
        location=location,
        imaging_rate=imaging_rate,
        manifold=manifold,
        conversion=conversion,
        unit=unit,
        reference_frame=reference_frame,
        origin_coords=origin_coords,
        origin_coords_unit=origin_coords_unit,
        grid_spacing=grid_spacing,
        grid_spacing_unit=grid_spacing_unit,
    )


def mock_TwoPhotonSeries(
    name=None,
    imaging_plane=mock_ImagingPlane(),
    data=np.ones((20, 5, 5)),
    rate=50.0,
    unit="n.a.",
    format=None,
    field_of_view=None,
    pmt_gain=None,
    scan_line_rate=None,
    external_file=None,
    starting_frame=[0],
    bits_per_pixel=None,
    dimension=None,
    resolution=-1.0,
    conversion=1.0,
    timestamps=None,
    starting_time=None,
    comments="no comments",
    description="no description",
    control=None,
    control_description=None,
    device=None,
):
    return TwoPhotonSeries(
        name=name if name is not None else name_generator("TwoPhotonSeries"),
        imaging_plane=imaging_plane,
        data=data,
        unit=unit,
        format=format,
        field_of_view=field_of_view,
        pmt_gain=pmt_gain,
        scan_line_rate=scan_line_rate,
        external_file=external_file,
        starting_frame=starting_frame,
        bits_per_pixel=bits_per_pixel,
        dimension=dimension,
        resolution=resolution,
        conversion=conversion,
        timestamps=timestamps,
        starting_time=starting_time,
        rate=rate,
        comments=comments,
        description=description,
        control=control,
        control_description=control_description,
        device=device,
    )


def mock_PlaneSegmentation(
    description="no description",
    imaging_plane=mock_ImagingPlane(),
    name=None,
    reference_images=None,
    n_rois=5,
):
    plane_segmentation = PlaneSegmentation(
        description=description,
        imaging_plane=imaging_plane,
        name=name if name is not None else name_generator("PlaneSegmentation"),
        reference_images=reference_images,
    )

    for _ in range(n_rois):
        plane_segmentation.add_roi(image_mask=np.zeros((10, 10)))

    return plane_segmentation


def mock_ImageSegmentation(
    plane_segmentations=None, name="ImageSegmentation",
):
    return ImageSegmentation(
        plane_segmentations=plane_segmentations or [mock_PlaneSegmentation()],
        name=name,
    )


def mock_RoiResponseSeries(
    name=None,
    data=None,
    unit="n.a.",
    rois=None,
    resolution=-1.0,
    conversion=1.0,
    timestamps=None,
    starting_time=None,
    rate=50.0,
    comments="no comments",
    description="no description",
    control=None,
    control_description=None,
    n_rois=5,
):
    return RoiResponseSeries(
        name=name if name is not None else name_generator("RoiResponseSeries"),
        data=data if data is not None else np.ones((30, 5)),
        unit=unit,
        rois=rois
        or DynamicTableRegion(
            name="rois",
            description="rois",
            table=mock_PlaneSegmentation(n_rois=n_rois),
            data=list(range(n_rois)),
        ),
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


def mock_DfOverF(roi_response_series=None, name=None):
    return DfOverF(
        roi_response_series=roi_response_series or [mock_RoiResponseSeries()],
        name=name if name is not None else name_generator("DfOverF"),
    )


def mock_Fluorescence(roi_response_series=None, name=None):
    return Fluorescence(
        roi_response_series=roi_response_series or [mock_RoiResponseSeries()],
        name=name if name is not None else name_generator("Fluorescence"),
    )
