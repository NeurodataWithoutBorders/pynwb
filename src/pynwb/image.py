import numpy as np
from collections import Iterable

from form.utils import docval, popargs

from .base import Interface, TimeSeries, _default_resolution, _default_conversion
from .core import NWBContainer

@register_class('ImageSeries', CORE_NAMESPACE)
class ImageSeries(TimeSeries):
    '''
    General image data that is common between acquisition and stimulus time series.
    The image data can be stored in the HDF5 file or it will be stored as an external image file.
    '''

    __nwbfields__ = ('bits_per_pixel',
                     'dimension',
                     'external_file',
                     'starting_frame',
                     'format')

    _ancestry = "TimeSeries,ImageSeries"
    _help = "Storage object for time-series 2-D image data"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'external_file', 'type': Iterable, 'doc': 'Path or URL to one or more external file(s). Field only present if format=external. Either external_file or data must be specified, but not both.'},
            {'name': 'starting_frame', 'type': Iterable, 'doc': 'Each entry is the frame number in the corresponding external_file variable. This serves as an index to what frames each file contains.'},
            {'name': 'format', 'type': str, 'doc': 'Format of image. Three types: 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.'},
            {'name': 'bits_per_pixel', 'type': float, 'doc': 'Number of bit per image pixel', 'default': np.nan},
            {'name': 'dimension', 'type': Iterable, 'doc': 'Number of pixels on x, y, (and z) axes.', 'default': [np.nan]},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default': None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default': None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit = popargs('name', 'source', 'data', 'unit', kwargs)
        bits_per_pixel, dimension, external_file, starting_frame, format = popargs('bits_per_pixel', 'dimension', 'external_file', 'starting_frame', 'format', kwargs)
        super(ImageSeries, self).__init__(name, source, data, unit, **kwargs)
        self.bits_per_pixel = bits_per_pixel
        self.dimension = dimension
        self.external_file = external_file
        self.starting_frame = starting_frame
        self.format = format


@register_class('IndexSeries', CORE_NAMESPACE)
class IndexSeries(TimeSeries):
    '''
    Stores indices to image frames stored in an ImageSeries. The purpose of the ImageIndexSeries is to allow
    a static image stack to be stored somewhere, and the images in the stack to be referenced out-of-order.
    This can be for the display of individual images, or of movie segments (as a movie is simply a series of
    images). The data field stores the index of the frame in the referenced ImageSeries, and the timestamps
    array indicates when that image was displayed.
    '''

    __nwbfields__ = ('index_timeseries',)

    _ancestry = "TimeSeries,IndexSeries"
    _help = "A sequence that is generated from an existing image stack. Frames can be presented in an arbitrary order. The data[] field stores frame number in reference stack."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'index_timeseries', 'type': TimeSeries, 'doc': 'HDF5 link to TimeSeries containing images that are indexed.'},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit = popargs('name', 'source', 'data', 'unit', kwargs)
        index_timeseries = popargs('index_timeseries', kwargs)
        super(IndexSeries, self).__init__(name, source, data, unit, **kwargs)
        self.index_timeseries = index_timeseries

@register_class('ImageMaskSeries', CORE_NAMESPACE)
class ImageMaskSeries(ImageSeries):
    '''
    An alpha mask that is applied to a presented visual stimulus. The data[] array contains an array
    of mask values that are applied to the displayed image. Mask values are stored as RGBA. Mask
    can vary with time. The timestamps array indicates the starting time of a mask, and that mask
    pattern continues until it's explicitly changed.
    '''

    __nwbfields__ = ('masked_imageseries',)

    _ancestry = "TimeSeries,ImageSeries,ImageMaskSeries"
    _help = "An alpha mask that is applied to a presented visual stimulus."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'masked_imageseries', 'type': ImageSeries, 'doc': 'Link to ImageSeries that mask is applied to.'},

            {'name': 'external_file', 'type': Iterable, 'doc': 'Path or URL to one or more external file(s). Field only present if format=external. Either external_file or data must be specified, but not both.'},
            {'name': 'starting_frame', 'type': Iterable, 'doc': 'Each entry is the frame number in the corresponding external_file variable. This serves as an index to what frames each file contains.'},
            {'name': 'format', 'type': str, 'doc': 'Format of image. Three types: 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.'},
            {'name': 'bits_per_pixel', 'type': float, 'doc': 'Number of bit per image pixel', 'default': np.nan},
            {'name': 'dimension', 'type': Iterable, 'doc': 'Number of pixels on x, y, (and z) axes.', 'default': [np.nan]},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit, external_file, starting_frame, format = popargs('name', 'source', 'data', 'unit', 'external_file', 'starting_frame', 'format', kwargs)
        masked_imageseries = popargs('masked_imageseries', kwargs)
        super(ImageMaskSeries, self).__init__(name, source, data, unit, external_file, starting_frame, format, **kwargs)
        self.masked_imageseries = masked_imageseries

@register_class('OpticalSeries', CORE_NAMESPACE)
class OpticalSeries(ImageSeries):
    '''
    Image data that is presented or recorded. A stimulus template movie will be stored only as an
    image. When the image is presented as stimulus, additional data is required, such as field of
    view (eg, how much of the visual field the image covers, or how what is the area of the target
    being imaged). If the OpticalSeries represents acquired imaging data, orientation is also
    important.
    '''

    __nwbfields__ = ('distance',
                     'field_of_view',
                     'orientation')

    _ancestry = "TimeSeries,ImageSeries,OpticalSeries"
    _help = "Time-series image stack for optical recording or stimulus."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'distance', 'type': float, 'doc': 'Distance from camera/monitor to target/eye.'},
            {'name': 'field_of_view', 'type': (list, np.ndarray, 'TimeSeries'), 'doc': 'Width, height and depth of image, or imaged area (meters).'},
            {'name': 'orientation', 'type': str, 'doc': 'Description of image relative to some reference frame (e.g., which way is up). Must also specify frame of reference.'},

            {'name': 'external_file', 'type': Iterable, 'doc': 'Path or URL to one or more external file(s). Field only present if format=external. Either external_file or data must be specified, but not both.'},
            {'name': 'starting_frame', 'type': Iterable, 'doc': 'Each entry is the frame number in the corresponding external_file variable. This serves as an index to what frames each file contains.'},
            {'name': 'format', 'type': str, 'doc': 'Format of image. Three types: 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.'},
            {'name': 'bits_per_pixel', 'type': float, 'doc': 'Number of bit per image pixel', 'default': np.nan},
            {'name': 'dimension', 'type': Iterable, 'doc': 'Number of pixels on x, y, (and z) axes.', 'default': [np.nan]},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit, external_file, starting_frame, format = popargs('name', 'source', 'data', 'unit', 'external_file', 'starting_frame', 'format', kwargs)
        distance, field_of_view, orientation = popargs('distance', 'field_of_view', 'orientation', kwargs)
        super(OpticalSeries, self).__init__(name, source, data, unit, external_file, starting_frame, format, **kwargs)
        self.distance = distance
        self.field_of_view = field_of_view
        self.orientation = orientation

@register_class('ROI', CORE_NAMESPACE)
class ROI(NWBContainer):
    """
    """

    __nwbfields__ = ('name',
                     'roi_description',
                     'pix_mask',
                     'pix_mask_weight',
                     'img_mask')

    @docval({'name': 'name', 'type': str, 'doc': 'name of ROI.'},
            {'name': 'roi_description', 'type': str, 'doc': 'Description of this ROI.'},
            {'name': 'pix_mask', 'type': Iterable, 'doc': 'List of pixels (x,y) that compose the mask.'},
            {'name': 'pix_mask_weight', 'type': Iterable, 'doc': 'Weight of each pixel listed in pix_mask.'},
            {'name': 'img_mask', 'type': Iterable, 'doc': 'ROI mask, represented in 2D ([y][x]) intensity image.'},
            {'name': 'reference_images', 'type': ImageSeries, 'doc': 'One or more image stacks that the masks apply to (can be oneelement stack).'})
    def __init__(self, **kwargs):
        name, roi_description, pix_mask, pix_mask_weight, img_mask = popargs('name', 'roi_description', 'pix_mask', 'pix_mask_weight', 'img_mask', kwargs)
        super(ROI, self).__init__(**kwargs)
        self.name = name
        self.roi_description = roi_description
        self.pix_mask = pix_mask
        self.pix_mask_weight = pix_mask_weight
        self.img_mask = img_mask

@register_class('OpticalChannel', CORE_NAMESPACE)
class OpticalChannel(NWBContainer):
    """
    """

    __nwbfields__ = ('description',
                     'emission_lambda')

    @docval({'name': 'description', 'type': str, 'doc': 'Any notes or comments about the channel.'},
            {'name': 'emission_lambda', 'type': str, 'doc': 'Emission lambda for channel.'},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        description, emission_lambda, parent = popargs("description", "emission_lambda", "parent", kwargs)
        super(OpticalChannel, self).__init__(parent=parent)
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

    @docval({'name': 'optical_channel', 'type': OpticalChannel, 'doc': 'One of possibly many groups storing channelspecific data.'},
            {'name': 'description', 'type': str, 'doc': 'Description of this ImagingPlane.'},
            {'name': 'device', 'type': str, 'doc': 'Name of device in /general/devices'},
            {'name': 'excitation_lambda', 'type': str, 'doc': 'Excitation wavelength.'},
            {'name': 'imaging_rate', 'type': str, 'doc': 'Rate images are acquired, in Hz.'},
            {'name': 'indicator', 'type': str, 'doc': 'Calcium indicator'},
            {'name': 'location', 'type': str, 'doc': 'Location of image plane.'},
            {'name': 'manifold', 'type': Iterable, 'doc': 'Physical position of each pixel. height, weight, x, y, z.'},
            {'name': 'conversion', 'type': float, 'doc': 'Multiplier to get from stored values to specified unit (e.g., 1e-3 for millimeters)'},
            {'name': 'unit', 'type': str, 'doc': 'Base unit that coordinates are stored in (e.g., Meters).'},
            {'name': 'reference_frame', 'type': str, 'doc': 'Describes position and reference frame of manifold based on position of first element in manifold.'},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        optical_channel, description, device, excitation_lambda, imaging_rate, indicator, location, manifold, conversion, unit, reference_frame, parent = popargs('optical_channel', 'description', 'device', 'excitation_lambda', 'imaging_rate', 'indicator', 'location', 'manifold', 'conversion', 'unit', 'reference_frame', 'parent', kwargs)
        super(ImagingPlane, self).__init__(parent=parent)
        self.optical_channel = optical_channel
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

@register_class('PlaneSegmentation', CORE_NAMESPACE)
class PlaneSegmentation(NWBContainer):
    """
    """

    __nwbfields__ = ('name',
                     'description',
                     'roi_list',
                     'imaging_plane',
                     'reference_images')

    @docval({'name': 'name', 'type': str, 'doc': 'name of PlaneSegmentation.'},
            {'name': 'description', 'type': str, 'doc': 'Description of image plane, recording wavelength, depth, etc.'},
            {'name': 'roi_list', 'type': Iterable, 'doc': 'List of ROIs in this imaging plane.'},
            {'name': 'imaging_plane', 'type': ImagingPlane, 'doc': 'link to ImagingPlane group from which this TimeSeries data was generated.'},
            {'name': 'reference_images', 'type': ImageSeries, 'doc': 'One or more image stacks that the masks apply to (can be oneelement stack).'})
    def __init__(self, **kwargs):
        name, description, roi_list, imaging_plane, reference_images = popargs('name', 'description', 'roi_list', 'imaging_plane', 'reference_images', kwargs)
        super(PlaneSegmentation, self).__init__(**kwargs)
        self.name = name
        self.description = description
        self.roi_list = roi_list
        self.imaging_plane = imaging_plane
        self.reference_images = reference_images

@register_class('ImageSegmentation', CORE_NAMESPACE)
class ImageSegmentation(Interface):
    """
    Stores pixels in an image that represent different regions of interest (ROIs) or masks. All
    segmentation for a given imaging plane is stored together, with storage for multiple imaging
    planes (masks) supported. Each ROI is stored in its own subgroup, with the ROI group
    containing both a 2D mask and a list of pixels that make up this mask. Segments can also be
    used for masking neuropil. If segmentation is allowed to change with time, a new imaging plane
    (or module) is required and ROI names should remain consistent between them.
    """

    __nwbfields__ = ('plane_segmentation',)

    _help = "Stores groups of pixels that define regions of interest from one or more imaging planes"

    @docval({'name': 'source', 'type': str, 'doc': 'The source of the data represented in this Module Interface.'},
            {'name': 'plane_segmentation', 'type': PlaneSegmentation, 'doc': 'ImagePlane class.'})
    def __init__(self, **kwargs):
        source, plane_segmentation = popargs('source', 'plane_segmentation', kwargs)
        super(ImageSegmentation, self).__init__(source, **kwargs)
        self.plane_segmentation = plane_segmentation
