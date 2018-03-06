from collections import Iterable
from six import with_metaclass
import numpy as np

from .form.utils import docval, popargs, fmt_docval_args, ExtenderMeta

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, _default_resolution, _default_conversion
from .image import ImageSeries
from .core import NWBContainer, MultiContainerInterface, VectorData, VectorIndex, IndexedVector


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
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
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


_roit_docval = [
    {'name': 'pixel_mask_region', 'type': RegionSlicer, 'help': 'a region into a PixelMasks'},
    {'name': 'image_mask_region', 'type': RegionSlicer, 'help': 'a region into an ImageMasks'},
]


class ROITable(NWBTable):

    @docval({'name': 'data', 'type': ('array_data', 'data'), 'doc': 'the source of the data', 'default': list()})
    def __init__(self, **kwargs):
        data = getargs('data', kwargs)
        colnames = [i['name'] for i in _roit_docval]
        colnames.append('group_ref')
        super(ElectrodeTable, self).__init__(colnames, 'rois', data)

    @docval(*_roit_docval)
    def add_row(self, **kwargs):
        call_docval_func(super(ROITable, self).add_row, kwargs)

    def __getitem__(self, idx):
        return ROI(super(ROITable, self).__getitem__(idx))


class ROI(object):
    """
    A class for defining a region of interest (ROI)
    """

    @docval({'name': 'row', 'type': (dict, np.void), 'doc': 'the ROITable row'})
    def __init__(self, **kwargs):
        self.__row = getargs('row', kwargs)

    @property
    def image_mask(self):
        return self.__row['image_mask_region'][:]

    @property
    def pixel_mask(self):
        return self.__row['pixel_mask_region'][:]


@register_class('PlaneSegmentation', CORE_NAMESPACE)
class PlaneSegmentation(MultiContainerInterface):
    """
    """

    __nwbfields__ = ('description',
                     'rois',
                     'pixel_mask',
                     'image_mask',
                     'imaging_plane',
                     'reference_images')

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'description', 'type': str,
             'doc': 'Description of image plane, recording wavelength, depth, etc.'},
            {'name': 'imaging_plane', 'type': ImagingPlane,
             'doc': 'the ImagingPlane this ROI applies to'},
            {'name': 'name', 'type': str, 'doc': 'name of PlaneSegmentation.', 'default': None},
            {'name': 'reference_images', 'type': (ImageSeries, list, dict, tuple), 'default': None,
             'doc': 'One or more image stacks that the masks apply to (can be oneelement stack).'},
            {'name': 'rois', 'type': (ROITable, Iterable), 'default': None,
             'doc': 'the table holding references to pixel and image masks'},
            {'name': 'pixel_mask', 'type': ('array_data', 'data', VectorData), 'default': None,
             'doc': 'a concatenated list of pixel masks for all ROIs stored in this PlaneSegmenation'},
            {'name': 'image_mask', 'type': ('array_data'), 'default': None,
             'doc': 'an image mask for each ROI in this PlaneSegmentation'})
    def __init__(self, **kwargs):
        description, imaging_plane, reference_images, rois, pm, image_mask = popargs(
            'description', 'imaging_plane', 'reference_images', 'rois', 'pixel_mask', 'image_mask', kwargs)
        if kwargs.get('name') is None:
            kwargs['name'] = imaging_plane.name
        pargs, pkwargs = fmt_docval_args(super(PlaneSegmentation, self).__init__, kwargs)
        super(PlaneSegmentation, self).__init__(*pargs, **pkwargs)
        self.description = description
        self.imaging_plane = imaging_plane
        self.reference_images = reference_images
        self.pixel_mask = pm
        self.image_mask = image_mask
        self.roi_table = ROITable() if rois is None else rois
        self.__rois = dict()

    @docval({'name': 'pixel_mask', 'type': int,
             'doc': 'the index of the ROI in roi_ids to retrieve the pixel mask for'},
            {'name': 'image_mask', 'type': int,
             'doc': 'the index of the ROI in roi_ids to retrieve the pixel mask for'})
    def add_roi(self, **kwargs):
        pixel_mask, image_mask = getargs('pixel_mask', 'image_mask', kwargs)
        n_rois = len(self.roi_table)
        im_region = get_region_slicer(self.image_mask, [n_rois])
        self.image_mask.append(image_mask)
        n_pixels = len(self.pixel_mask)
        self.pixel_mask.extend(pixel_mask)
        pm_region = get_region_slice(self.pixel_mask, slice(n_pixels, n_pixels + len(pixel_mask)))
        self.roi_table.add_row(pm_region, im_region)
        return n_rois+1

    @docval({'name': 'index', 'type': int,
             'doc': 'the index of the ROI to retrieve the pixel mask for'})
    def get_pixel_mask(self, **kwargs):
        index = getargs('index', kwargs)
        return self.roi_table[index]['pixel_mask'][:]

    @docval({'name': 'index', 'type': int,
             'doc': 'the index of the ROI to retrieve the image mask for'})
    def get_image_mask(self, **kwargs):
        index = getargs('index', kwargs)
        return self.roi_table[index]['image_mask'][:]

    @docval({'name': 'index', 'type': int,
             'doc': 'the index of the ROI in roi_ids'})
    def get_roi(self, **kwargs):
        index = getargs('index', kwargs)
        if index in self.__rois:
            return self.__rois[index]
        else:
            return self.__rois.setdefault(index, ROI(self.roi_table[index]))


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

    @docval({'name': 'imaging_plane', 'type': ImagingPlane,'doc': 'the ImagingPlane this ROI applies to'},
            {'name': 'description', 'type': str,
             'doc': 'Description of image plane, recording wavelength, depth, etc.', 'default': None},
            {'name': 'source', 'type': str, 'doc': 'the source of the data','default': None},
            {'name': 'name', 'type': str, 'doc': 'name of PlaneSegmentation.', 'default': None})
    def add_segmentation(self, **kwargs):
        kwargs.setdefault('source', self.source)
        kwargs.setdefault('description', imaging_plane.description)
        return self.add_plane_segmentation(**kwargs)


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
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
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
        roi_names, segmentation_interface = popargs('roi_names', 'segmentation_interface', kwargs)
        pargs, pkwargs = fmt_docval_args(super(RoiResponseSeries, self).__init__, kwargs)
        super(RoiResponseSeries, self).__init__(*pargs, **pkwargs)
        self.roi_names = roi_names
        self.segmentation_interface = segmentation_interface


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
