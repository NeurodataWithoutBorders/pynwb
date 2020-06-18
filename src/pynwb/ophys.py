from collections.abc import Iterable
import numpy as np
import warnings

from hdmf.utils import docval, getargs, popargs, call_docval_func, get_docval

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries
from .image import ImageSeries
from .core import NWBContainer, MultiContainerInterface, NWBDataInterface
from hdmf.common import DynamicTable, DynamicTableRegion
from .device import Device


@register_class('OpticalChannel', CORE_NAMESPACE)
class OpticalChannel(NWBContainer):
    """An optical channel used to record from an imaging plane."""

    __nwbfields__ = ('description',
                     'emission_lambda')

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this electrode'},  # required
            {'name': 'description', 'type': str, 'doc': 'Any notes or comments about the channel.'},  # required
            {'name': 'emission_lambda', 'type': 'float', 'doc': 'Emission wavelength for channel, in nm.'})  # required
    def __init__(self, **kwargs):
        description, emission_lambda = popargs("description", "emission_lambda", kwargs)
        call_docval_func(super(OpticalChannel, self).__init__, kwargs)
        self.description = description
        self.emission_lambda = emission_lambda


@register_class('ImagingPlane', CORE_NAMESPACE)
class ImagingPlane(NWBContainer):
    """An imaging plane and its metadata."""

    __nwbfields__ = ({'name': 'optical_channel', 'child': True},
                     'description',
                     'device',
                     'excitation_lambda',
                     'imaging_rate',
                     'indicator',
                     'location',
                     'manifold',
                     'conversion',
                     'unit',
                     'reference_frame')

    @docval(*get_docval(NWBContainer.__init__, 'name'),  # required
            {'name': 'optical_channel', 'type': (list, OpticalChannel),  # required
             'doc': 'One of possibly many groups storing channel-specific data.'},
            {'name': 'description', 'type': str, 'doc': 'Description of this ImagingPlane.'},  # required
            {'name': 'device', 'type': Device, 'doc': 'the device that was used to record'},  # required
            {'name': 'excitation_lambda', 'type': 'float', 'doc': 'Excitation wavelength in nm.'},  # required
            {'name': 'indicator', 'type': str, 'doc': 'Calcium indicator'},  # required
            {'name': 'location', 'type': str, 'doc': 'Location of image plane.'},  # required
            {'name': 'imaging_rate', 'type': 'float',
             'doc': 'Rate images are acquired, in Hz. If the corresponding TimeSeries is present, the rate should be '
                    'stored there instead.', 'default': None},
            {'name': 'manifold', 'type': 'array_data',
             'doc': ('DEPRECATED: Physical position of each pixel. size=("height", "width", "xyz"). '
                     'Deprecated in favor of origin_coords and grid_spacing.'),
             'default': None},
            {'name': 'conversion', 'type': 'float',
             'doc': ('DEPRECATED: Multiplier to get from stored values to specified unit (e.g., 1e-3 for millimeters) '
                     'Deprecated in favor of origin_coords and grid_spacing.'),
             'default': 1.0},
            {'name': 'unit', 'type': str,
             'doc': 'DEPRECATED: Base unit that coordinates are stored in (e.g., Meters). '
                    'Deprecated in favor of origin_coords_unit and grid_spacing_unit.',
             'default': 'meters'},
            {'name': 'reference_frame', 'type': str,
             'doc': 'Describes position and reference frame of manifold based on position of first element '
                    'in manifold.',
             'default': None},
            {'name': 'origin_coords', 'type': 'array_data',
             'doc': 'Physical location of the first element of the imaging plane (0, 0) for 2-D data or (0, 0, 0) for '
                    '3-D data. See also reference_frame for what the physical location is relative to (e.g., bregma).',
             'default': None},
            {'name': 'origin_coords_unit', 'type': str,
             'doc': "Measurement units for origin_coords. The default value is 'meters'.",
             'default': 'meters'},
            {'name': 'grid_spacing', 'type': 'array_data',
             'doc': "Space between pixels in (x, y) or voxels in (x, y, z) directions, in the specified unit. Assumes "
                    "imaging plane is a regular grid. See also reference_frame to interpret the grid.",
             'default': None},
            {'name': 'grid_spacing_unit', 'type': str,
             'doc': "Measurement units for grid_spacing. The default value is 'meters'.",
             'default': 'meters'})
    def __init__(self, **kwargs):
        optical_channel, description, device, excitation_lambda, imaging_rate, \
            indicator, location, manifold, conversion, unit, reference_frame, origin_coords, origin_coords_unit, \
            grid_spacing, grid_spacing_unit = popargs(
                'optical_channel', 'description', 'device', 'excitation_lambda',
                'imaging_rate', 'indicator', 'location', 'manifold', 'conversion',
                'unit', 'reference_frame', 'origin_coords', 'origin_coords_unit', 'grid_spacing', 'grid_spacing_unit',
                kwargs)
        call_docval_func(super(ImagingPlane, self).__init__, kwargs)
        self.optical_channel = optical_channel if isinstance(optical_channel, list) else [optical_channel]
        self.description = description
        self.device = device
        self.excitation_lambda = excitation_lambda
        self.imaging_rate = imaging_rate
        self.indicator = indicator
        self.location = location
        if manifold is not None:
            warnings.warn("The 'manifold' argument is deprecated in favor of 'origin_coords' and 'grid_spacing'.",
                          DeprecationWarning)
        if conversion != 1.0:
            warnings.warn("The 'conversion' argument is deprecated in favor of 'origin_coords' and 'grid_spacing'.",
                          DeprecationWarning)
        if unit != 'meters':
            warnings.warn("The 'unit' argument is deprecated in favor of 'origin_coords_unit' and 'grid_spacing_unit'.",
                          DeprecationWarning)
        self.manifold = manifold
        self.conversion = conversion
        self.unit = unit
        self.reference_frame = reference_frame
        self.origin_coords = origin_coords
        self.origin_coords_unit = origin_coords_unit
        self.grid_spacing = grid_spacing
        self.grid_spacing_unit = grid_spacing_unit


@register_class('TwoPhotonSeries', CORE_NAMESPACE)
class TwoPhotonSeries(ImageSeries):
    """Image stack recorded over time from 2-photon microscope."""

    __nwbfields__ = ('field_of_view',
                     'imaging_plane',
                     'pmt_gain',
                     'scan_line_rate')

    @docval(*get_docval(ImageSeries.__init__, 'name'),  # required
            {'name': 'imaging_plane', 'type': ImagingPlane, 'doc': 'Imaging plane class/pointer.'},  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': ([None] * 3, [None] * 4),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames',
             'default': None},
            *get_docval(ImageSeries.__init__, 'unit', 'format'),
            {'name': 'field_of_view', 'type': (Iterable, TimeSeries), 'shape': ((2, ), (3, )),
             'doc': 'Width, height and depth of image, or imaged area (meters).', 'default': None},
            {'name': 'pmt_gain', 'type': 'float', 'doc': 'Photomultiplier gain.', 'default': None},
            {'name': 'scan_line_rate', 'type': 'float',
             'doc': 'Lines imaged per second. This is also stored in /general/optophysiology but is kept '
                    'here as it is useful information for analysis, and so good to be stored w/ the actual data.',
             'default': None},
            *get_docval(ImageSeries.__init__, 'external_file', 'starting_frame', 'bits_per_pixel',
                        'dimension', 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description'))
    def __init__(self, **kwargs):
        field_of_view, imaging_plane, pmt_gain, scan_line_rate = popargs(
            'field_of_view', 'imaging_plane', 'pmt_gain', 'scan_line_rate', kwargs)
        call_docval_func(super(TwoPhotonSeries, self).__init__, kwargs)
        self.field_of_view = field_of_view
        self.imaging_plane = imaging_plane
        self.pmt_gain = pmt_gain
        self.scan_line_rate = scan_line_rate


@register_class('CorrectedImageStack', CORE_NAMESPACE)
class CorrectedImageStack(NWBDataInterface):
    """
    An image stack where all frames are shifted (registered) to a common coordinate system, to
    account for movement and drift between frames. Note: each frame at each point in time is
    assumed to be 2-D (has only x & y dimensions).
    """

    __nwbfields__ = ({'name': 'corrected', 'child': True},
                     {'name': 'xy_translation', 'child': True},
                     'original')

    @docval({'name': 'name', 'type': str,
             'doc': 'The name of this CorrectedImageStack container', 'default': 'CorrectedImageStack'},
            {'name': 'corrected', 'type': ImageSeries,
             'doc': 'Image stack with frames shifted to the common coordinates.'},
            {'name': 'original', 'type': ImageSeries,
             'doc': 'Link to image series that is being registered.'},
            {'name': 'xy_translation', 'type': TimeSeries,
             'doc': 'Stores the x,y delta necessary to align each frame to the common coordinates, '
                    'for example, to align each frame to a reference image.'})
    def __init__(self, **kwargs):
        corrected, original, xy_translation = popargs('corrected', 'original', 'xy_translation', kwargs)
        call_docval_func(super(CorrectedImageStack, self).__init__, kwargs)
        self.corrected = corrected
        self.original = original
        self.xy_translation = xy_translation


@register_class('MotionCorrection', CORE_NAMESPACE)
class MotionCorrection(MultiContainerInterface):
    """
    A collection of corrected images stacks.
    """

    __clsconf__ = {
        'add': 'add_corrected_image_stack',
        'get': 'get_corrected_image_stack',
        'create': 'create_corrected_image_stack',
        'type': CorrectedImageStack,
        'attr': 'corrected_images_stacks'
    }


@register_class('PlaneSegmentation', CORE_NAMESPACE)
class PlaneSegmentation(DynamicTable):
    """
    Stores pixels in an image that represent different regions of interest (ROIs)
    or masks. All segmentation for a given imaging plane is stored together, with
    storage for multiple imaging planes (masks) supported. Each ROI is stored in its
    own subgroup, with the ROI group containing both a 2D mask and a list of pixels
    that make up this mask. Segments can also be used for masking neuropil. If segmentation
    is allowed to change with time, a new imaging plane (or module) is required and
    ROI names should remain consistent between them.
    """

    __fields__ = ('imaging_plane',
                  {'name': 'reference_images', 'child': True})

    __columns__ = (
        {'name': 'image_mask', 'description': 'Image masks for each ROI'},
        {'name': 'pixel_mask', 'description': 'Pixel masks for each ROI', 'index': True},
        {'name': 'voxel_mask', 'description': 'Voxel masks for each ROI', 'index': True}
    )

    @docval({'name': 'description', 'type': str,  # required
             'doc': 'Description of image plane, recording wavelength, depth, etc.'},
            {'name': 'imaging_plane', 'type': ImagingPlane,  # required
             'doc': 'the ImagingPlane this ROI applies to'},
            {'name': 'name', 'type': str, 'doc': 'name of PlaneSegmentation.', 'default': None},
            {'name': 'reference_images', 'type': (ImageSeries, list, dict, tuple), 'default': None,
             'doc': 'One or more image stacks that the masks apply to (can be oneelement stack).'},
            *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames'))
    def __init__(self, **kwargs):
        imaging_plane, reference_images = popargs('imaging_plane', 'reference_images', kwargs)
        if kwargs.get('name') is None:
            kwargs['name'] = imaging_plane.name
        columns, colnames = getargs('columns', 'colnames', kwargs)
        call_docval_func(super(PlaneSegmentation, self).__init__, kwargs)
        self.imaging_plane = imaging_plane
        if isinstance(reference_images, ImageSeries):
            reference_images = (reference_images,)
        self.reference_images = reference_images

    @docval({'name': 'pixel_mask', 'type': 'array_data', 'default': None,
             'doc': 'pixel mask for 2D ROIs: [(x1, y1, weight1), (x2, y2, weight2), ...]',
             'shape': (None, 3)},
            {'name': 'voxel_mask', 'type': 'array_data', 'default': None,
             'doc': 'voxel mask for 3D ROIs: [(x1, y1, z1, weight1), (x2, y2, z2, weight2), ...]',
             'shape': (None, 4)},
            {'name': 'image_mask', 'type': 'array_data', 'default': None,
             'doc': 'image with the same size of image where positive values mark this ROI',
             'shape': [[None]*2, [None]*3]},
            {'name': 'id', 'type': int, 'doc': 'the ID for the ROI', 'default': None},
            allow_extra=True)
    def add_roi(self, **kwargs):
        """Add a Region Of Interest (ROI) data to this"""
        pixel_mask, voxel_mask, image_mask = popargs('pixel_mask', 'voxel_mask', 'image_mask', kwargs)
        if image_mask is None and pixel_mask is None and voxel_mask is None:
            raise ValueError("Must provide 'image_mask' and/or 'pixel_mask'")
        rkwargs = dict(kwargs)
        if image_mask is not None:
            rkwargs['image_mask'] = image_mask
        if pixel_mask is not None:
            rkwargs['pixel_mask'] = pixel_mask
        if voxel_mask is not None:
            rkwargs['voxel_mask'] = voxel_mask
        return super(PlaneSegmentation, self).add_row(**rkwargs)

    @staticmethod
    def pixel_to_image(pixel_mask):
        """Converts a 2D pixel_mask of a ROI into an image_mask."""
        image_matrix = np.zeros(np.shape(pixel_mask))
        npmask = np.asarray(pixel_mask)
        x_coords = npmask[:, 0].astype(np.int)
        y_coords = npmask[:, 1].astype(np.int)
        weights = npmask[:, -1]
        image_matrix[y_coords, x_coords] = weights
        return image_matrix

    @staticmethod
    def image_to_pixel(image_mask):
        """Converts an image_mask of a ROI into a pixel_mask"""
        pixel_mask = []
        it = np.nditer(image_mask, flags=['multi_index'])
        while not it.finished:
            weight = it[0][()]
            if weight > 0:
                x = it.multi_index[0]
                y = it.multi_index[1]
                pixel_mask.append([x, y, weight])
            it.iternext()
        return pixel_mask

    @docval({'name': 'description', 'type': str, 'doc': 'a brief description of what the region is'},
            {'name': 'region', 'type': (slice, list, tuple), 'doc': 'the indices of the table', 'default': slice(None)},
            {'name': 'name', 'type': str, 'doc': 'the name of the ROITableRegion', 'default': 'rois'})
    def create_roi_table_region(self, **kwargs):
        return call_docval_func(self.create_region, kwargs)


@register_class('ImageSegmentation', CORE_NAMESPACE)
class ImageSegmentation(MultiContainerInterface):
    """
    Stores pixels in an image that represent different regions of interest (ROIs) or masks. All
    segmentation for a given imaging plane is stored together, with storage for multiple imaging
    planes (masks) supported. Each ROI is stored in its own subgroup, with the ROI group
    containing both a 2D mask and a list of pixels that make up this mask. Segments can also be
    used for masking neuropil. If segmentation is allowed to change with time, a new imaging plane
    (or module) is required and ROI names should remain consistent between them.
    """
    __clsconf__ = {
        'attr': 'plane_segmentations',
        'type': PlaneSegmentation,
        'add': 'add_plane_segmentation',
        'get': 'get_plane_segmentation',
        'create': 'create_plane_segmentation'
    }

    @docval({'name': 'imaging_plane', 'type': ImagingPlane, 'doc': 'the ImagingPlane this ROI applies to'},
            {'name': 'description', 'type': str,
             'doc': 'Description of image plane, recording wavelength, depth, etc.', 'default': None},
            {'name': 'name', 'type': str, 'doc': 'name of PlaneSegmentation.', 'default': None})
    def add_segmentation(self, **kwargs):
        kwargs.setdefault('description', kwargs['imaging_plane'].description)
        return self.create_plane_segmentation(**kwargs)


@register_class('RoiResponseSeries', CORE_NAMESPACE)
class RoiResponseSeries(TimeSeries):
    '''
    ROI responses over an imaging plane. Each column in data should correspond to
    the signal from one ROI.
    '''

    __nwbfields__ = ({'name': 'rois', 'child': True},)

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),  # required
             'shape': ((None, ), (None, None)),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            *get_docval(TimeSeries.__init__, 'unit'),
            {'name': 'rois', 'type': DynamicTableRegion,  # required
             'doc': 'a table region corresponding to the ROIs that were used to generate this data'},
            *get_docval(TimeSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description'))
    def __init__(self, **kwargs):
        rois = popargs('rois', kwargs)
        call_docval_func(super(RoiResponseSeries, self).__init__, kwargs)
        self.rois = rois


@register_class('DfOverF', CORE_NAMESPACE)
class DfOverF(MultiContainerInterface):
    """
    dF/F information about a region of interest (ROI). Storage hierarchy of dF/F should be the same
    as for segmentation (ie, same names for ROIs and for image planes).
    """

    __clsconf__ = {
        'attr': 'roi_response_series',
        'type': RoiResponseSeries,
        'add': 'add_roi_response_series',
        'get': 'get_roi_response_series',
        'create': 'create_roi_response_series'
    }


@register_class('Fluorescence', CORE_NAMESPACE)
class Fluorescence(MultiContainerInterface):
    """
    Fluorescence information about a region of interest (ROI). Storage hierarchy of fluorescence
    should be the same as for segmentation (ie, same names for ROIs and for image planes).
    """

    __clsconf__ = {
        'attr': 'roi_response_series',
        'type': RoiResponseSeries,
        'add': 'add_roi_response_series',
        'get': 'get_roi_response_series',
        'create': 'create_roi_response_series'
    }
