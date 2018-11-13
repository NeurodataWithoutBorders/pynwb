from collections import Iterable
import numpy as np

from .form.utils import docval, getargs, popargs, fmt_docval_args, call_docval_func

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, _default_resolution, _default_conversion
from .image import ImageSeries
from .core import NWBContainer, MultiContainerInterface, DynamicTable, DynamicTableRegion, ElementIdentifiers
from .device import Device


@register_class('OpticalChannel', CORE_NAMESPACE)
class OpticalChannel(NWBContainer):
    """
    """

    __nwbfields__ = ('description',
                     'emission_lambda')

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this electrode'},
            {'name': 'description', 'type': str, 'doc': 'Any notes or comments about the channel.'},
            {'name': 'emission_lambda', 'type': float, 'doc': 'Emission lambda for channel.'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        description, emission_lambda, parent = popargs("description", "emission_lambda", "parent", kwargs)
        pargs, pkwargs = fmt_docval_args(super(OpticalChannel, self).__init__, kwargs)
        super(OpticalChannel, self).__init__(*pargs, **pkwargs)
        self.description = description
        self.emission_lambda = emission_lambda


@register_class('ImagingPlane', CORE_NAMESPACE)
class ImagingPlane(NWBContainer):
    """
    """

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

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this electrode'},
            {'name': 'optical_channel', 'type': (list, OpticalChannel),
             'doc': 'One of possibly many groups storing channelspecific data.'},
            {'name': 'description', 'type': str, 'doc': 'Description of this ImagingPlane.'},
            {'name': 'device', 'type': Device, 'doc': 'the device that was used to record'},
            {'name': 'excitation_lambda', 'type': float, 'doc': 'Excitation wavelength in nm.'},
            {'name': 'imaging_rate', 'type': float, 'doc': 'Rate images are acquired, in Hz.'},
            {'name': 'indicator', 'type': str, 'doc': 'Calcium indicator'},
            {'name': 'location', 'type': str, 'doc': 'Location of image plane.'},
            {'name': 'manifold', 'type': Iterable,
             'doc': 'Physical position of each pixel. size=("height", "width", "xyz").',
             'default': None},
            {'name': 'conversion', 'type': float,
             'doc': 'Multiplier to get from stored values to specified unit (e.g., 1e-3 for millimeters)',
             'default': None},
            {'name': 'unit', 'type': str, 'doc': 'Base unit that coordinates are stored in (e.g., Meters).',
             'default': None},
            {'name': 'reference_frame', 'type': str,
             'doc': 'Describes position and reference frame of manifold based on position of first element \
             in manifold.', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        optical_channel, description, device, excitation_lambda, imaging_rate, \
            indicator, location, manifold, conversion, unit, reference_frame, parent = popargs(
                'optical_channel', 'description', 'device', 'excitation_lambda',
                'imaging_rate', 'indicator', 'location', 'manifold', 'conversion',
                'unit', 'reference_frame', 'parent', kwargs)
        pargs, pkwargs = fmt_docval_args(super(ImagingPlane, self).__init__, kwargs)
        super(ImagingPlane, self).__init__(*pargs, **pkwargs)
        self.optical_channel = optical_channel if isinstance(optical_channel, list) else [optical_channel]
        self.description = description
        self.device = device
        self.excitation_lambda = excitation_lambda
        self.imaging_rate = imaging_rate
        self.indicator = indicator
        self.location = location
        self.manifold = manifold
        self.conversion = conversion
        self.unit = unit
        self.reference_frame = reference_frame


@register_class('TwoPhotonSeries', CORE_NAMESPACE)
class TwoPhotonSeries(ImageSeries):
    """
    A special case of optical imaging.
    """

    __nwbfields__ = ('field_of_view',
                     'imaging_plane',
                     'pmt_gain',
                     'scan_line_rate')

    _help = "Image stack recorded from 2-photon microscope."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'imaging_plane', 'type': ImagingPlane, 'doc': 'Imaging plane class/pointer.'},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': ([None] * 3, [None] * 4),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames',
             'default': None},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)', 'default': None},
            {'name': 'format', 'type': str,
             'doc': 'Format of image. Three types: 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.',
             'default': None},
            {'name': 'field_of_view', 'type': (Iterable, TimeSeries), 'shape': ((2, ), (3, )),
             'doc': 'Width, height and depth of image, or imaged area (meters).', 'default': None},
            {'name': 'pmt_gain', 'type': float, 'doc': 'Photomultiplier gain.', 'default': None},
            {'name': 'scan_line_rate', 'type': float,
             'doc': 'Lines imaged per second. This is also stored in /general/optophysiology but is kept \
             here as it is useful information for analysis, and so good to be stored w/ the actual data.',
             'default': None},
            {'name': 'external_file', 'type': Iterable,
             'doc': 'Path or URL to one or more external file(s). Field only present if format=external. \
             Either external_file or data must be specified, but not both.', 'default': None},
            {'name': 'starting_frame', 'type': Iterable,
             'doc': 'Each entry is the frame number in the corresponding external_file variable. \
             This serves as an index to what frames each file contains.', 'default': None},
            {'name': 'bits_per_pixel', 'type': int, 'doc': 'Number of bit per image pixel', 'default': None},
            {'name': 'dimension', 'type': Iterable,
             'doc': 'Number of pixels on x, y, (and z) axes.', 'default': [np.nan]},
            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) \
            between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries), 'shape': (None, ),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},
            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default': 'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        field_of_view, imaging_plane, pmt_gain, scan_line_rate = popargs(
            'field_of_view', 'imaging_plane', 'pmt_gain', 'scan_line_rate', kwargs)
        pargs, pkwargs = fmt_docval_args(super(TwoPhotonSeries, self).__init__, kwargs)
        super(TwoPhotonSeries, self).__init__(*pargs, **pkwargs)
        self.field_of_view = field_of_view
        self.imaging_plane = imaging_plane
        self.pmt_gain = pmt_gain
        self.scan_line_rate = scan_line_rate


@register_class('CorrectedImageStack', CORE_NAMESPACE)
class CorrectedImageStack(NWBContainer):
    """
    An image stack where all frames are shifted (registered) to a common coordinate system, to
    account for movement and drift between frames. Note: each frame at each point in time is
    assumed to be 2-D (has only x & y dimensions).
    """

    __nwbfields__ = ('corrected',
                     'original',
                     'xy_translation')

    _help = ""

    @docval({'name': 'name', 'type': str,
             'doc': 'The name of this CorrectedImageStack container', 'default': 'CorrectedImageStack'},
            {'name': 'corrected', 'type': ImageSeries,
             'doc': 'Image stack with frames shifted to the common coordinates.'},
            {'name': 'original', 'type': ImageSeries,
             'doc': 'Link to image series that is being registered.'},
            {'name': 'xy_translation', 'type': TimeSeries,
             'doc': 'Stores the x,y delta necessary to align each frame to the common coordinates,\
             for example, to align each frame to a reference image.'})
    def __init__(self, **kwargs):
        corrected, original, xy_translation = popargs('corrected', 'original', 'xy_translation', kwargs)
        super(CorrectedImageStack, self).__init__(**kwargs)
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

    _help = "Image stacks whose frames have been shifted (registered) to account for motion."


@register_class('PlaneSegmentation', CORE_NAMESPACE)
class PlaneSegmentation(DynamicTable):
    """
    Image segmentation of a specific imaging plane
    """

    __nwbfields__ = ('description',
                     'imaging_plane',
                     {'name': 'reference_images', 'child': True})

    __columns__ = (
        {'name': 'image_mask', 'description': 'Image masks for each ROI'},
        {'name': 'pixel_mask', 'description': 'Pixel masks for each ROI', 'index': True},
        {'name': 'voxel_mask', 'description': 'Voxel masks for each ROI', 'index': True}
    )

    @docval({'name': 'description', 'type': str,
             'doc': 'Description of image plane, recording wavelength, depth, etc.'},
            {'name': 'imaging_plane', 'type': ImagingPlane,
             'doc': 'the ImagingPlane this ROI applies to'},
            {'name': 'name', 'type': str, 'doc': 'name of PlaneSegmentation.', 'default': None},
            {'name': 'reference_images', 'type': (ImageSeries, list, dict, tuple), 'default': None,
             'doc': 'One or more image stacks that the masks apply to (can be oneelement stack).'},
            {'name': 'id', 'type': ('array_data', ElementIdentifiers), 'doc': 'the identifiers for this table',
             'default': None},
            {'name': 'columns', 'type': (tuple, list), 'doc': 'the columns in this table', 'default': None},
            {'name': 'colnames', 'type': 'array_data', 'doc': 'the names of the columns in this table',
            'default': None})
    def __init__(self, **kwargs):
        imaging_plane, reference_images = popargs('imaging_plane', 'reference_images', kwargs)
        if kwargs.get('name') is None:
            kwargs['name'] = imaging_plane.name
        columns, colnames = getargs('columns', 'colnames', kwargs)
        pargs, pkwargs = fmt_docval_args(super(PlaneSegmentation, self).__init__, kwargs)
        super(PlaneSegmentation, self).__init__(*pargs, **pkwargs)
        self.imaging_plane = imaging_plane
        self.reference_images = reference_images

    @docval({'name': 'pixel_mask', 'type': 'array_data', 'default': None,
             'doc': 'pixel mask for 2D ROIs: [(x1, y1, weight1), (x2, y2, weight2), ...]',
             'shape': (None, 3)},
            {'name': 'voxel_mask', 'type': 'array_data', 'default': None,
             'doc': 'voxel mask for 3D ROIs: [(x1, y1, z1, weight1), (x2, y2, z1, weight2), ...]',
             'shape': (None, 4)},
            {'name': 'image_mask', 'type': 'array_data', 'default': None,
             'doc': 'image with the same size of image where positive values mark this ROI',
             'shape': [[None]*2, [None]*3]},
            {'name': 'id', 'type': int, 'help': 'the ID for the ROI', 'default': None},
            allow_extra=True)
    def add_roi(self, **kwargs):
        """
        Add ROI data to this
        """
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

    _help = "Stores groups of pixels that define regions of interest from one or more imaging planes"

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
    ROI responses over an imaging plane. Each row in data[] should correspond to the signal from one ROI.
    '''

    __nwbfields__ = ({'name': 'rois', 'child': True},)

    _help = "ROI responses over an imaging plane. Each row in data[] should correspond to the signal from one no ROI."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'rois', 'type': DynamicTableRegion,
             'doc': 'a table region corresponding to the ROIs that were used to generate this data'},

            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element by to convert to volts', 'default': _default_conversion},
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},
            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset',
             'default': 'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        rois = popargs('rois', kwargs)
        pargs, pkwargs = fmt_docval_args(super(RoiResponseSeries, self).__init__, kwargs)
        super(RoiResponseSeries, self).__init__(*pargs, **pkwargs)
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

    _help = "Df/f over time of one or more ROIs. TimeSeries names should correspond to imaging plane names"


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

    _help = "Fluorescence over time of one or more ROIs. TimeSeries names should correspond to imaging plane names."
