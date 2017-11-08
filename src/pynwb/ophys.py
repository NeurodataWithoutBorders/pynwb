from collections import Iterable
import numpy as np

from .form.utils import docval, popargs, fmt_docval_args

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, _default_resolution, _default_conversion
from .image import ImageSeries
from .core import NWBContainer


@register_class('OpticalChannel', CORE_NAMESPACE)
class OpticalChannel(NWBContainer):
    """
    """

    __nwbfields__ = ('description',
                     'emission_lambda')

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this electrode'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'description', 'type': str, 'doc': 'Any notes or comments about the channel.'},
            {'name': 'emission_lambda', 'type': str, 'doc': 'Emission lambda for channel.'},
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

    __nwbfields__ = ('optical_channel',
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
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'optical_channel', 'type': (list, OpticalChannel),
             'doc': 'One of possibly many groups storing channelspecific data.'},
            {'name': 'description', 'type': str, 'doc': 'Description of this ImagingPlane.'},
            {'name': 'device', 'type': str, 'doc': 'Name of device in /general/devices'},
            {'name': 'excitation_lambda', 'type': str, 'doc': 'Excitation wavelength.'},
            {'name': 'imaging_rate', 'type': str, 'doc': 'Rate images are acquired, in Hz.'},
            {'name': 'indicator', 'type': str, 'doc': 'Calcium indicator'},
            {'name': 'location', 'type': str, 'doc': 'Location of image plane.'},
            {'name': 'manifold', 'type': Iterable, 'doc': 'Physical position of each pixel. height, weight, x, y, z.',
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

    _ancestry = "TimeSeries,ImageSeries,TwoPhotonSeries"
    _help = "Image stack recorded from 2-photon microscope."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': (Iterable, TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'imaging_plane', 'type': ImagingPlane, 'doc': 'Imaging plane class/pointer.'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)', 'default': None},
            {'name': 'format', 'type': str,
             'doc': 'Format of image. Three types: 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.',
             'default': None},
            {'name': 'field_of_view', 'type': (Iterable, TimeSeries),
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
            {'name': 'timestamps', 'type': (TimeSeries, Iterable),
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


@register_class('ROI', CORE_NAMESPACE)
class ROI(NWBContainer):
    """
    A class for defining a region of interest (ROI)
    """

    __nwbfields__ = ('roi_description',
                     'pix_mask',
                     'pix_mask_weight',
                     'img_mask')

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this ROI'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'roi_description', 'type': str, 'doc': 'Description of this ROI.'},
            {'name': 'pix_mask', 'type': Iterable, 'doc': 'List of pixels (x,y) that compose the mask.'},
            {'name': 'pix_mask_weight', 'type': Iterable, 'doc': 'Weight of each pixel listed in pix_mask.'},
            {'name': 'img_mask', 'type': Iterable, 'doc': 'ROI mask, represented in 2D ([y][x]) intensity image.'},
            {'name': 'reference_images', 'type': (ImageSeries, str),
             'doc': 'One or more image stacks that the masks apply to (can be oneelement stack).'})
    def __init__(self, **kwargs):
        roi_description, pix_mask, pix_mask_weight, img_mask = popargs(
            'roi_description', 'pix_mask', 'pix_mask_weight', 'img_mask', kwargs)
        pargs, pkwargs = fmt_docval_args(super(ROI, self).__init__, kwargs)
        super(ROI, self).__init__(*pargs, **pkwargs)
        self.roi_description = roi_description
        self.pix_mask = pix_mask
        self.pix_mask_weight = pix_mask_weight
        self.img_mask = img_mask


@register_class('PlaneSegmentation', CORE_NAMESPACE)
class PlaneSegmentation(NWBContainer):
    """
    """

    __nwbfields__ = ('description',
                     'roi_list',
                     'imaging_plane',
                     'reference_images')

    @docval({'name': 'name', 'type': str, 'doc': 'name of PlaneSegmentation.'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'description', 'type': str,
             'doc': 'Description of image plane, recording wavelength, depth, etc.'},
            {'name': 'roi_list', 'type': (Iterable, ROI), 'doc': 'List of ROIs in this imaging plane.'},
            {'name': 'imaging_plane', 'type': ImagingPlane,
             'doc': 'link to ImagingPlane group from which this TimeSeries data was generated.'},
            {'name': 'reference_images', 'type': ImageSeries,
             'doc': 'One or more image stacks that the masks apply to (can be oneelement stack).'})
    def __init__(self, **kwargs):
        description, roi_list, imaging_plane, reference_images = popargs(
            'description', 'roi_list', 'imaging_plane', 'reference_images', kwargs)
        pargs, pkwargs = fmt_docval_args(super(PlaneSegmentation, self).__init__, kwargs)
        super(PlaneSegmentation, self).__init__(*pargs, **pkwargs)
        self.description = description
        self.roi_list = roi_list
        self.imaging_plane = imaging_plane
        self.reference_images = reference_images


@register_class('ImageSegmentation', CORE_NAMESPACE)
class ImageSegmentation(NWBContainer):
    """
    Stores pixels in an image that represent different regions of interest (ROIs) or masks. All
    segmentation for a given imaging plane is stored together, with storage for multiple imaging
    planes (masks) supported. Each ROI is stored in its own subgroup, with the ROI group
    containing both a 2D mask and a list of pixels that make up this mask. Segments can also be
    used for masking neuropil. If segmentation is allowed to change with time, a new imaging plane
    (or module) is required and ROI names should remain consistent between them.
    """

    __nwbfields__ = ('plane_segmentations',)

    _help = "Stores groups of pixels that define regions of interest from one or more imaging planes"

    @docval({'name': 'source', 'type': str, 'doc': 'The source of the data represented in this Module Interface.'},
            {'name': 'plane_segmentations', 'type': (PlaneSegmentation, list),
             'doc': 'PlaneSegmentation with the description of the image plane.'},
            {'name': 'name', 'type': str, 'doc': 'the name of this ImageSegmentation container',
             'default': 'ImageSegmentation'})
    def __init__(self, **kwargs):
        plane_segmentations = popargs('plane_segmentations', kwargs)

        if isinstance(plane_segmentations, PlaneSegmentation):
            plane_segmentations = [plane_segmentations]

        pargs, pkwargs = fmt_docval_args(super(ImageSegmentation, self).__init__, kwargs)
        super(ImageSegmentation, self).__init__(*pargs, **pkwargs)
        self.plane_segmentations = plane_segmentations


@register_class('RoiResponseSeries', CORE_NAMESPACE)
class RoiResponseSeries(TimeSeries):
    '''
    ROI responses over an imaging plane. Each row in data[] should correspond to the signal from one ROI.
    '''

    __nwbfields__ = ('roi_names',
                     'segmentation_interface')

    _ancestry = "TimeSeries,ImageSeries,ImageMaskSeries"
    _help = "ROI responses over an imaging plane. Each row in data[] should correspond to the signal from one no ROI."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': (Iterable, TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'roi_names', 'type': Iterable,
             'doc': 'List of ROIs represented, one name for each row of data[].'},
            {'name': 'segmentation_interface', 'type': ImageSegmentation, 'doc': 'Link to ImageSegmentation.'},

            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},
            {'name': 'timestamps', 'type': (TimeSeries, Iterable),
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
        roi_names, segmentation_interface = popargs('roi_names', 'segmentation_interface', kwargs)
        pargs, pkwargs = fmt_docval_args(super(RoiResponseSeries, self).__init__, kwargs)
        super(RoiResponseSeries, self).__init__(*pargs, **pkwargs)
        self.roi_names = roi_names
        self.segmentation_interface = segmentation_interface


@register_class('DfOverF', CORE_NAMESPACE)
class DfOverF(NWBContainer):
    """
    dF/F information about a region of interest (ROI). Storage hierarchy of dF/F should be the same
    as for segmentation (ie, same names for ROIs and for image planes).
    """

    __nwbfields__ = ('roi_response_series',)

    _help = "Df/f over time of one or more ROIs. TimeSeries names should correspond to imaging plane names"

    @docval({'name': 'source', 'type': str, 'doc': 'The source of the data represented in this Module Interface.'},
            {'name': 'roi_response_series', 'type': (RoiResponseSeries, list),
             'doc': 'RoiResponseSeries or any subtype.'},
            {'name': 'name', 'type': str, 'doc': 'the name of this DfOverF container', 'default': 'DfOverF'})
    def __init__(self, **kwargs):
        roi_response_series = popargs('roi_response_series', kwargs)
        pargs, pkwargs = fmt_docval_args(super(DfOverF, self).__init__, kwargs)
        super(DfOverF, self).__init__(*pargs, **pkwargs)
        self.roi_response_series = roi_response_series


@register_class('Fluorescence', CORE_NAMESPACE)
class Fluorescence(NWBContainer):
    """
    Fluorescence information about a region of interest (ROI). Storage hierarchy of fluorescence
    should be the same as for segmentation (ie, same names for ROIs and for image planes).
    """

    __nwbfields__ = ('roi_response_series',)

    _help = "Fluorescence over time of one or more ROIs. TimeSeries names should correspond to imaging plane names."

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'roi_response_series', 'type': (RoiResponseSeries, list),
             'doc': 'RoiResponseSeries or any subtype.'},
            {'name': 'name', 'type': str, 'doc': 'the name of this Fluorescence container', 'default': 'Fluorescence'})
    def __init__(self, **kwargs):
        roi_response_series = popargs('roi_response_series', kwargs)
        pargs, pkwargs = fmt_docval_args(super(Fluorescence, self).__init__, kwargs)
        super(Fluorescence, self).__init__(*pargs, **pkwargs)
        self.roi_response_series = roi_response_series
