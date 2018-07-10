from collections import Iterable
from h5py import RegionReference
import numpy as np

from .form.utils import docval, getargs, popargs, fmt_docval_args, call_docval_func
from .form.data_utils import RegionSlicer
from .form import get_region_slicer

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, _default_resolution, _default_conversion
from .image import ImageSeries
from .core import NWBContainer, MultiContainerInterface, NWBData, VectorData, NWBTable, NWBTableRegion


@register_class('OpticalChannel', CORE_NAMESPACE)
class OpticalChannel(NWBContainer):
    """
    """

    __nwbfields__ = ('description',
                     'emission_lambda')

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this electrode'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
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
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'optical_channel', 'type': (list, OpticalChannel),
             'doc': 'One of possibly many groups storing channelspecific data.'},
            {'name': 'description', 'type': str, 'doc': 'Description of this ImagingPlane.'},
            {'name': 'device', 'type': str, 'doc': 'Name of device in /general/devices'},
            {'name': 'excitation_lambda', 'type': float, 'doc': 'Excitation wavelength.'},
            {'name': 'imaging_rate', 'type': str, 'doc': 'Rate images are acquired, in Hz.'},
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

    _ancestry = "TimeSeries,ImageSeries,TwoPhotonSeries"
    _help = "Image stack recorded from 2-photon microscope."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'imaging_plane', 'type': ImagingPlane, 'doc': 'Imaging plane class/pointer.'},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames',
             'default': None},
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
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries),
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
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
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


_roit_docval = [
    {'name': 'name', 'type': str, 'help': 'a name for this ROI'},
    {'name': 'pixel_mask', 'type': RegionSlicer, 'help': 'a region into a PixelMasks'},
    {'name': 'image_mask', 'type': RegionSlicer, 'help': 'a region into an ImageMasks'},
]


@register_class('ROITable', CORE_NAMESPACE)
class ROITable(NWBTable):

    __columns__ = _roit_docval

    __defaultname__ = 'rois'


@register_class('ROITableRegion', CORE_NAMESPACE)
class ROITableRegion(NWBTableRegion):
    '''A subsetting of an ElectrodeTable'''

    __nwbfields__ = ('description',)

    @docval({'name': 'table', 'type': ROITable, 'doc': 'the ElectrodeTable this region applies to'},
            {'name': 'region', 'type': (slice, list, tuple, RegionReference), 'doc': 'the indices of the table'},
            {'name': 'description', 'type': str, 'doc': 'a brief description of what this electrode is'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': 'electrodes'})
    def __init__(self, **kwargs):
        call_docval_func(super(ROITableRegion, self).__init__, kwargs)
        self.description = getargs('description', kwargs)


@register_class('PixelMasks', CORE_NAMESPACE)
class PixelMasks(VectorData):

    @docval({'name': 'data', 'type': ('array_data', 'data'), 'doc': 'the pixel mask data'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': 'pixel_masks'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(PixelMasks, self).__init__, kwargs)


@register_class('ImageMasks', CORE_NAMESPACE)
class ImageMasks(NWBData):

    @docval({'name': 'data', 'type': ('array_data', 'data'), 'doc': 'the image mask data'},
            {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': 'image_masks'},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object,
            'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        call_docval_func(super(ImageMasks, self).__init__, kwargs)


@register_class('PlaneSegmentation', CORE_NAMESPACE)
class PlaneSegmentation(NWBContainer):
    """
    Image segmentation of a specific imaging plane
    """

    __nwbfields__ = ('description',
                     {'name': 'rois', 'child': True},
                     {'name': 'pixel_masks', 'child': True},
                     {'name': 'image_masks', 'child': True},
                     'imaging_plane',
                     {'name': 'reference_images', 'child': True})

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'description', 'type': str,
             'doc': 'Description of image plane, recording wavelength, depth, etc.'},
            {'name': 'imaging_plane', 'type': ImagingPlane,
             'doc': 'the ImagingPlane this ROI applies to'},
            {'name': 'name', 'type': str, 'doc': 'name of PlaneSegmentation.', 'default': None},
            {'name': 'reference_images', 'type': (ImageSeries, list, dict, tuple), 'default': None,
             'doc': 'One or more image stacks that the masks apply to (can be oneelement stack).'},
            {'name': 'rois', 'type': ROITable, 'default': None,
             'doc': 'the table holding references to pixel and image masks'},
            {'name': 'pixel_masks', 'type': ('array_data', 'data', PixelMasks), 'default': list(),
             'doc': 'a concatenated list of pixel masks for all ROIs stored in this PlaneSegmenation'},
            {'name': 'image_masks', 'type': ('array_data', ImageMasks), 'default': list(),
             'doc': 'an image mask for each ROI in this PlaneSegmentation'})
    def __init__(self, **kwargs):
        description, imaging_plane, reference_images, rois, pm, im = popargs(
            'description', 'imaging_plane', 'reference_images', 'rois', 'pixel_masks', 'image_masks', kwargs)
        if kwargs.get('name') is None:
            kwargs['name'] = imaging_plane.name
        pargs, pkwargs = fmt_docval_args(super(PlaneSegmentation, self).__init__, kwargs)
        super(PlaneSegmentation, self).__init__(*pargs, **pkwargs)
        self.description = description
        self.imaging_plane = imaging_plane
        self.reference_images = reference_images
        self.pixel_masks = pm if isinstance(pm, PixelMasks) else PixelMasks(pm)
        self.image_masks = im if isinstance(im, ImageMasks) else ImageMasks(im)
        self.rois = ROITable() if rois is None else rois

    @docval({'name': 'name', 'type': str, 'help': 'a name for this ROI'},
            {'name': 'pixel_mask', 'type': 'array_data',
             'doc': 'the index of the ROI in roi_ids to retrieve the pixel mask for'},
            {'name': 'image_mask', 'type': 'array_data',
             'doc': 'the index of the ROI in roi_ids to retrieve the pixel mask for'})
    def add_roi(self, **kwargs):
        name, pixel_mask, image_mask = getargs('name', 'pixel_mask', 'image_mask', kwargs)
        n_rois = len(self.rois)
        im_region = get_region_slicer(self.image_masks, [n_rois])
        self.image_masks.append(image_mask)
        n_pixels = len(self.pixel_masks)
        self.pixel_masks.extend(pixel_mask)
        pm_region = get_region_slicer(self.pixel_masks, slice(n_pixels, n_pixels + len(pixel_mask)))
        self.rois.add_row(name, pm_region, im_region)
        return n_rois+1

    @docval({'name': 'index', 'type': int,
             'doc': 'the index of the ROI to retrieve the pixel mask for'})
    def get_pixel_mask(self, **kwargs):
        index = getargs('index', kwargs)
        return self.rois[index]['pixel_mask']

    @docval({'name': 'index', 'type': int,
             'doc': 'the index of the ROI to retrieve the image mask for'})
    def get_image_mask(self, **kwargs):
        index = getargs('index', kwargs)
        return self.rois[index]['image_mask']

    @docval({'name': 'description', 'type': str, 'doc': 'a brief description of what this electrode is'},
            {'name': 'names', 'type': (list, tuple), 'doc': 'the names of the ROIs', 'default': None},
            {'name': 'region', 'type': (slice, list, tuple, RegionReference), 'doc': 'the indices of the table',
             'default': None},
            {'name': 'name', 'type': str, 'doc': 'the name of the ROITableRegion', 'default': 'rois'})
    def create_roi_table_region(self, **kwargs):
        desc = getargs('description', kwargs)
        name = getargs('name', kwargs)
        region = getargs('region', kwargs)
        names = getargs('names', kwargs)
        if region is None and names is None:
            msg = "must provide 'region' or 'names'"
            raise ValueError(msg)
        elif names is not None:
            region = list()
            for n in names:
                idx = self.rois.which(name=n)
                if len(idx) == 0:
                    msg = "no ROI named '%s'" % n
                    raise ValueError(msg)
                region.append(idx[0])
            # collapse into a slice if we can
            consecutive = True
            for i in range(1, len(region)):
                if region[i] - region[i-1] != 1:
                    consecutive = False
                    break
            if consecutive:
                region = slice(region[0], region[-1]+1)
        return ROITableRegion(self.rois, region, desc, name)


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
            {'name': 'source', 'type': str, 'doc': 'the source of the data', 'default': None},
            {'name': 'name', 'type': str, 'doc': 'name of PlaneSegmentation.', 'default': None})
    def add_segmentation(self, **kwargs):
        kwargs.setdefault('source', self.source)
        kwargs.setdefault('description', kwargs['imaging_plane'].description)
        return self.create_plane_segmentation(**kwargs)


@register_class('RoiResponseSeries', CORE_NAMESPACE)
class RoiResponseSeries(TimeSeries):
    '''
    ROI responses over an imaging plane. Each row in data[] should correspond to the signal from one ROI.
    '''

    __nwbfields__ = ({'name': 'rois', 'child': True},)

    _ancestry = "TimeSeries,ImageSeries,ImageMaskSeries"
    _help = "ROI responses over an imaging plane. Each row in data[] should correspond to the signal from one no ROI."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'rois', 'type': ROITableRegion,
             'doc': 'a table region corresponding to the ROIs that were used to generate this data'},

            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},
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
