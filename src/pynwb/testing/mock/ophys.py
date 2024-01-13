from typing import Optional, Sequence

import numpy as np

from hdmf.common.table import DynamicTableRegion

from ... import NWBFile, ProcessingModule
from ...device import Device
from ...ophys import (
    RoiResponseSeries,
    OpticalChannel,
    ImagingPlane,
    OnePhotonSeries,
    TwoPhotonSeries,
    PlaneSegmentation,
    ImageSegmentation,
    DfOverF,
    Fluorescence,
)
from .device import mock_Device
from .utils import name_generator


def mock_OpticalChannel(
    name: Optional[str] = None,
    description: str = "description",
    emission_lambda: float = 500.0,
    nwbfile: Optional[NWBFile] = None,
) -> OpticalChannel:
    optical_channel = OpticalChannel(
        name=name or name_generator("OpticalChannel"), description=description, emission_lambda=emission_lambda,
    )

    if nwbfile is not None:
        mock_ImagingPlane(nwbfile=nwbfile, optical_channel=optical_channel)

    return optical_channel


def mock_ImagingPlane(
    name: Optional[str] = None,
    optical_channel: Optional[OpticalChannel] = None,
    description: str = "description",
    device: Optional[Device] = None,
    excitation_lambda: float = 500.0,
    indicator: str = "indicator",
    location: str = "unknown",
    imaging_rate: float = 30.0,
    manifold=None,
    conversion: float = 1.0,
    unit: str = "meters",
    reference_frame=None,
    origin_coords=None,
    origin_coords_unit: str = "meters",
    grid_spacing=None,
    grid_spacing_unit: str = "meters",
    nwbfile: Optional[NWBFile] = None,
) -> ImagingPlane:
    imaging_plane = ImagingPlane(
        name=name or name_generator("ImagingPlane"),
        optical_channel=optical_channel or mock_OpticalChannel(nwbfile=nwbfile),
        description=description,
        device=device or mock_Device(nwbfile=nwbfile),
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

    if nwbfile is not None:
        if "ophys" not in nwbfile.processing:
            nwbfile.create_processing_module("ophys", "ophys")
        nwbfile.add_imaging_plane(imaging_plane)

    return imaging_plane


def mock_OnePhotonSeries(
    name: Optional[str] = None,
    imaging_plane: Optional[ImagingPlane] = None,
    data=None,
    rate: Optional[float] = 50.0,
    unit: str = "n.a.",
    exposure_time=None,
    binning=None,
    power=None,
    intensity=None,
    format=None,
    pmt_gain=None,
    scan_line_rate=None,
    external_file=None,
    starting_frame=[0],
    bits_per_pixel=None,
    dimension=None,
    resolution=-1.0,
    conversion=1.0,
    offset=0.0,
    timestamps=None,
    starting_time=None,
    comments="no comments",
    description="no description",
    control=None,
    control_description=None,
    device=None,
    nwbfile: Optional[NWBFile] = None,
) -> OnePhotonSeries:
    one_photon_series = OnePhotonSeries(
        name=name if name is not None else name_generator("OnePhotonSeries"),
        imaging_plane=imaging_plane or mock_ImagingPlane(nwbfile=nwbfile),
        data=data if data is not None else np.ones((20, 5, 5)),
        unit=unit,
        exposure_time=exposure_time,
        binning=binning,
        power=power,
        intensity=intensity,
        format=format,
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
        offset=offset,
        rate=rate,
        comments=comments,
        description=description,
        control=control,
        control_description=control_description,
        device=device,
    )

    if nwbfile is not None:
        nwbfile.add_acquisition(one_photon_series)

    return one_photon_series


def mock_TwoPhotonSeries(
    name: Optional[str] = None,
    imaging_plane: Optional[ImagingPlane] = None,
    data=None,
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
    offset=0.0,
    timestamps=None,
    starting_time=None,
    comments="no comments",
    description="no description",
    control=None,
    control_description=None,
    device=None,
    nwbfile: Optional[NWBFile] = None,
) -> TwoPhotonSeries:
    two_photon_series = TwoPhotonSeries(
        name=name if name is not None else name_generator("TwoPhotonSeries"),
        imaging_plane=imaging_plane or mock_ImagingPlane(nwbfile=nwbfile),
        data=data if data is not None else np.ones((20, 5, 5)),
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
        offset=offset,
    )

    if nwbfile is not None:
        nwbfile.add_acquisition(two_photon_series)

    return two_photon_series


def mock_PlaneSegmentation(
    description: str = "no description",
    imaging_plane: Optional[ImagingPlane] = None,
    name: Optional[str] = None,
    reference_images=None,
    n_rois: int = 5,
    nwbfile: Optional[NWBFile] = None,
) -> PlaneSegmentation:
    plane_segmentation = PlaneSegmentation(
        description=description,
        imaging_plane=imaging_plane or mock_ImagingPlane(nwbfile=nwbfile),
        name=name if name is not None else name_generator("PlaneSegmentation"),
        reference_images=reference_images,
    )

    for _ in range(n_rois):
        plane_segmentation.add_roi(image_mask=np.zeros((10, 10)))

    if nwbfile is not None:
        if "ophys" not in nwbfile.processing:
            nwbfile.create_processing_module("ophys", "ophys")
        nwbfile.processing["ophys"].add(plane_segmentation)

    return plane_segmentation


def mock_ImageSegmentation(
    plane_segmentations: Optional[Sequence[PlaneSegmentation]] = None,
        name: Optional[str] = None,
        nwbfile: Optional[NWBFile] = None
) -> ImageSegmentation:
    image_segmentation = ImageSegmentation(
        plane_segmentations=plane_segmentations or [mock_PlaneSegmentation(nwbfile=nwbfile)],
        name=name or name_generator("ImageSegmentation"),
    )

    if nwbfile is not None:
        if "ophys" not in nwbfile.processing:
            nwbfile.create_processing_module("ophys", "ophys")

        nwbfile.processing["ophys"].add(image_segmentation)

    return image_segmentation


def mock_RoiResponseSeries(
    name: Optional[str] = None,
    data=None,
    unit: str = "n.a.",
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
    n_rois=None,
    plane_segmentation: Optional[PlaneSegmentation] = None,
    nwbfile: Optional[NWBFile] = None,
) -> RoiResponseSeries:
    if data is not None:
        if n_rois is not None and n_rois != data.shape[1]:
            raise ValueError("Argument conflict: n_rois does not match second dimension of data.")
        n_rois = data.shape[1]
    else:
        n_rois = 5

    plane_seg = plane_segmentation or mock_PlaneSegmentation(n_rois=n_rois, nwbfile=nwbfile)

    roi_response_series = RoiResponseSeries(
        name=name if name is not None else name_generator("RoiResponseSeries"),
        data=data if data is not None else np.ones((30, n_rois)),
        unit=unit,
        rois=rois
        or DynamicTableRegion(
            name="rois",
            description="rois",
            table=plane_seg,
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

    if nwbfile is not None:
        if "ophys" not in nwbfile.processing:
            nwbfile.create_processing_module("ophys", "ophys")

        if plane_seg.name not in nwbfile.processing["ophys"].data_interfaces:
            nwbfile.processing["ophys"].add(plane_seg)

        nwbfile.processing["ophys"].add(roi_response_series)

    return roi_response_series


def mock_DfOverF(
    roi_response_series: Optional[RoiResponseSeries] = None,
    name: Optional[str] = None,
    nwbfile: Optional[NWBFile] = None
) -> DfOverF:
    df_over_f = DfOverF(
        name=name if name is not None else name_generator("DfOverF"),
    )
    plane_seg = mock_PlaneSegmentation(nwbfile=nwbfile)

    if nwbfile is not None:
        if "ophys" not in nwbfile.processing:
            nwbfile.create_processing_module("ophys", "ophys")

        nwbfile.processing["ophys"].add(df_over_f)

    else:
        pm = ProcessingModule(name="ophys", description="ophys")
        pm.add(plane_seg)
        pm.add(df_over_f)

    df_over_f.add_roi_response_series(
        roi_response_series or mock_RoiResponseSeries(nwbfile=nwbfile, plane_segmentation=plane_seg)
    )
    return df_over_f


def mock_Fluorescence(
    roi_response_series: Optional[Sequence[RoiResponseSeries]] = None,
    name: Optional[str] = None,
    nwbfile: Optional[NWBFile] = None,
) -> Fluorescence:
    fluorescence = Fluorescence(
        name=name if name is not None else name_generator("Fluorescence"),
    )
    plane_seg = mock_PlaneSegmentation(nwbfile=nwbfile)

    if nwbfile is not None:
        if "ophys" not in nwbfile.processing:
            nwbfile.create_processing_module("ophys", "ophys")

        nwbfile.processing["ophys"].add(fluorescence)
    else:
        pm = ProcessingModule(name="ophys", description="ophys")
        pm.add(plane_seg)
        pm.add(fluorescence)

    fluorescence.add_roi_response_series(
        roi_response_series or mock_RoiResponseSeries(nwbfile=nwbfile, plane_segmentation=plane_seg)
    )

    return fluorescence
