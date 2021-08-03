import warnings
import numpy as np
from collections.abc import Iterable

from hdmf.utils import docval, getargs, popargs, call_docval_func, get_docval, get_data_shape

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, Image
from .core import NWBDataInterface
from .device import Device


@register_class('ImageSeries', CORE_NAMESPACE)
class ImageSeries(TimeSeries):
    '''
    General image data that is common between acquisition and stimulus time series.
    The image data can be stored in the HDF5 file or it will be stored as an external image file.
    '''

    __nwbfields__ = ('dimension',
                     'external_file',
                     'starting_frame',
                     'format',
                     'device')

    # value used when an ImageSeries is read and missing data
    DEFAULT_DATA = np.ndarray(shape=(0, 0, 0), dtype=np.uint8)
    # TODO: copy new docs from 2.4 schema

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': ([None] * 3, [None] * 4),
             'doc': ('The data values. Can be 3D or 4D. The first dimension must be time (frame). The second and third '
                     'dimensions represent x and y. The optional fourth dimension represents z. Either data or '
                     'external_file must be specified, but not both.')},
            {'name': 'unit', 'type': str,
             'doc': ('The unit of measurement of the image data, e.g., values between 0 and 255.')},
            {'name': 'format', 'type': str,
             'doc': 'Format of image. Three types: 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.',
             'default': None},
            {'name': 'external_file', 'type': ('array_data', 'data'),
             'doc': 'Path or URL to one or more external file(s). Field only present if format=external. '
                    'Either external_file or data must be specified, but not both.', 'default': None},
            {'name': 'starting_frame', 'type': Iterable,
             'doc': 'Each entry is the frame number in the corresponding external_file variable. '
                    'This serves as an index to what frames each file contains. If external_file is not '
                    'provided, then this value will be None', 'default': [0]},
            {'name': 'bits_per_pixel', 'type': int, 'doc': 'DEPRECATED: Number of bits per image pixel',
             'default': None},
            {'name': 'dimension', 'type': Iterable,
             'doc': 'Number of pixels on x, y, (and z) axes.', 'default': None},
            *get_docval(TimeSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description'),
            {'name': 'device', 'type': Device,
             'doc': 'Device used to capture the images/video.', 'default': None},)
    def __init__(self, **kwargs):
        bits_per_pixel, dimension, external_file, starting_frame, format, device = popargs(
            'bits_per_pixel', 'dimension', 'external_file', 'starting_frame', 'format', 'device', kwargs)
        name, data, unit = getargs('name', 'data', 'unit', kwargs)
        if data is not None and unit is None:
            raise ValueError("Must supply 'unit' argument when supplying 'data' to %s '%s'."
                             % (self.__class__.__name__, name))
        if external_file is None and data is None:
            raise ValueError("Must supply either external_file or data to %s '%s'."
                             % (self.__class__.__name__, name))
        if external_file is not None:
            msg = ("Storing external files in an ImageSeries is discouraged and will be deprecated in a future "
                   "major release. Use ExternalImageSeries instead.")
            warnings.warn(msg, PendingDeprecationWarning)
        if data is not None:
            data_shape = get_data_shape(data)
            if len(data_shape) == 4 and data_shape[3] > 3:
                # NOTE this check will not catch all uses of ImageSeries to store volumetric data. if the volume
                # has length <=3 in the z direction, then we cannot distinguish between volumetric data and
                # multi-channel data
                msg = ("Storing volumetric data in an ImageSeries is discouraged and will be deprecated in a future "
                       "major release. Use VolumeSeries instead.")
                warnings.warn(msg, PendingDeprecationWarning)

        # data and unit are required in TimeSeries, but allowed to be None here, so handle this specially
        if data is None:
            kwargs['data'] = ImageSeries.DEFAULT_DATA
        if unit is None:
            kwargs['unit'] = ImageSeries.DEFAULT_UNIT

        call_docval_func(super(ImageSeries, self).__init__, kwargs)

        self.bits_per_pixel = bits_per_pixel
        self.dimension = dimension
        self.external_file = external_file
        if external_file is not None:
            self.starting_frame = starting_frame
        else:
            self.starting_frame = None
        self.format = format
        self.device = device

    @property
    def bits_per_pixel(self):
        return self.fields.get('bits_per_pixel')

    @bits_per_pixel.setter
    def bits_per_pixel(self, val):
        if val is not None:
            warnings.warn("bits_per_pixel is no longer used", DeprecationWarning)
            self.fields['bits_per_pixel'] = val


@register_class('ExternalImageSeries', CORE_NAMESPACE)
class ExternalImageSeries(NWBDataInterface):
    '''
    General image data that is common between acquisition and stimulus time series.
    The image data can be stored in the HDF5 file or it will be stored as an external image file.
    '''

    __nwbfields__ = ('dimension',
                     'external_file',
                     'starting_frame',
                     'timestamps',
                     'timestamps_unit',
                     'interval',
                     'starting_time',
                     'starting_time_unit',
                     'rate',
                     'device')

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'external_file', 'type': ('array_data', 'data'),
             'doc': 'Path or URL to one or more external file(s). Field only present if format=external. '
                    'Either external_file or data must be specified, but not both.'},
            {'name': 'starting_frame', 'type': Iterable,
             'doc': 'Each entry is the frame number in the corresponding external_file variable. '
                    'This serves as an index to what frames each file contains. If external_file is not '
                    'provided, then this value will be None', 'default': [0]},
            {'name': 'dimension', 'type': Iterable,
             'doc': 'Number of pixels on x, y, (and z) axes.', 'default': None},
            {'name': 'timestamps', 'type': ('array_data', 'data', 'TimeSeries'), 'shape': (None,),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': 'float', 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': 'float', 'doc': 'Sampling rate in Hz', 'default': None},
            {'name': 'device', 'type': Device,
             'doc': 'Device used to capture the images/video.', 'default': None},)
    def __init__(self, **kwargs):
        dimension, external_file, starting_frame, timestamps, starting_time, rate, device = popargs(
            'dimension', 'external_file', 'starting_frame', 'timestamps', 'starting_time', 'rate', 'device', kwargs)

        call_docval_func(super().__init__, kwargs)

        if timestamps is not None:
            if rate is not None:
                raise ValueError('Specifying rate and timestamps is not supported.')
            if starting_time is not None:
                raise ValueError('Specifying starting_time and timestamps is not supported.')
            self.fields['timestamps'] = timestamps
            self.timestamps_unit = self.__time_unit
            self.interval = 1
            if isinstance(timestamps, TimeSeries):
                timestamps.__add_link('timestamp_link', self)
        elif rate is not None:
            self.rate = rate
            if starting_time is not None:
                self.starting_time = starting_time
            else:
                self.starting_time = 0.0
            self.starting_time_unit = self.__time_unit
        else:
            raise TypeError("either 'timestamps' or 'rate' must be specified")

        self.dimension = dimension
        self.external_file = external_file
        self.starting_frame = starting_frame
        self.device = device


@register_class('IndexSeries', CORE_NAMESPACE)
class IndexSeries(TimeSeries):
    '''
    Stores indices to image frames stored in an ImageSeries. The purpose of the IndexSeries is to allow
    a static image stack to be stored somewhere, and the images in the stack to be referenced out-of-order.
    This can be for the display of individual images, or of movie segments (as a movie is simply a series of
    images). The data field stores the index of the frame in the referenced ImageSeries, and the timestamps
    array indicates when that image was displayed.
    '''

    __nwbfields__ = ('indexed_timeseries',)

    # value used when an ImageSeries is read and missing data
    DEFAULT_UNIT = 'N/A'

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': (None, ),  # required
             'doc': ('The data values. Must be 1D, where the first dimension must be time (frame)')},
            {'name': 'indexed_timeseries', 'type': TimeSeries,  # required
             'doc': 'HDF5 link to TimeSeries containing images that are indexed.'},
            *get_docval(TimeSeries.__init__, 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description'))
    def __init__(self, **kwargs):
        indexed_timeseries = popargs('indexed_timeseries', kwargs)
        kwargs['unit'] = IndexSeries.DEFAULT_UNIT  # IndexSeries/data.unit has a fixed value of N/A in NWB 2.4.0
        super(IndexSeries, self).__init__(**kwargs)
        self.indexed_timeseries = indexed_timeseries


@register_class('ImageMaskSeries', CORE_NAMESPACE)
class ImageMaskSeries(ImageSeries):
    '''
    An alpha mask that is applied to a presented visual stimulus. The data[] array contains an array
    of mask values that are applied to the displayed image. Mask values are stored as RGBA. Mask
    can vary with time. The timestamps array indicates the starting time of a mask, and that mask
    pattern continues until it's explicitly changed.
    '''

    __nwbfields__ = ('masked_imageseries',)

    @docval(*get_docval(ImageSeries.__init__, 'name'),  # required
            {'name': 'masked_imageseries', 'type': ImageSeries,  # required
             'doc': 'Link to ImageSeries that mask is applied to.'},
            *get_docval(ImageSeries.__init__, 'data', 'unit', 'format', 'external_file', 'starting_frame',
                        'bits_per_pixel', 'dimension', 'resolution', 'conversion', 'timestamps', 'starting_time',
                        'rate', 'comments', 'description', 'control', 'control_description'),
            {'name': 'device', 'type': Device,
             'doc': ('Device used to capture the mask data. This field will likely not be needed. '
                     'The device used to capture the masked ImageSeries data should be stored in the ImageSeries.'),
             'default': None},)
    def __init__(self, **kwargs):
        masked_imageseries = popargs('masked_imageseries', kwargs)
        super(ImageMaskSeries, self).__init__(**kwargs)
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

    @docval(*get_docval(ImageSeries.__init__, 'name'),  # required
            {'name': 'distance', 'type': 'float', 'doc': 'Distance from camera/monitor to target/eye.'},  # required
            {'name': 'field_of_view', 'type': ('array_data', 'data', 'TimeSeries'), 'shape': ((2, ), (3, )),  # required
             'doc': 'Width, height and depth of image, or imaged area (meters).'},
            {'name': 'orientation', 'type': str,  # required
             'doc': 'Description of image relative to some reference frame (e.g., which way is up). '
                    'Must also specify frame of reference.'},
            {'name': 'data', 'type': ('array_data', 'data'), 'shape': ([None] * 3, [None, None, None, 3]),
             'doc': ('Images presented to subject, either grayscale or RGB. May be 3D or 4D. The first dimension must '
                     'be time (frame). The second and third dimensions represent x and y. The optional fourth '
                     'dimension must be length 3 and represents the RGB value for color images. Either data or '
                     'external_file must be specified, but not both.'),
             'default': None},
            *get_docval(ImageSeries.__init__, 'unit', 'format', 'external_file', 'starting_frame', 'bits_per_pixel',
                        'dimension', 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate', 'comments',
                        'description', 'control', 'control_description', 'device'))
    def __init__(self, **kwargs):
        distance, field_of_view, orientation = popargs('distance', 'field_of_view', 'orientation', kwargs)
        super(OpticalSeries, self).__init__(**kwargs)
        self.distance = distance
        self.field_of_view = field_of_view
        self.orientation = orientation


@register_class('GrayscaleImage', CORE_NAMESPACE)
class GrayscaleImage(Image):

    @docval(*get_docval(Image.__init__, 'name'),
            {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'Data of image. Must be 2D',
             'shape': (None, None)},
            *get_docval(Image.__init__, 'resolution', 'description'))
    def __init__(self, **kwargs):
        call_docval_func(super(GrayscaleImage, self).__init__, kwargs)


@register_class('RGBImage', CORE_NAMESPACE)
class RGBImage(Image):

    @docval(*get_docval(Image.__init__, 'name'),
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'Data of image. Must be 3D where the third dimension has length 3 and represents the RGB value',
             'shape': (None, None, 3)},
            *get_docval(Image.__init__, 'resolution', 'description'))
    def __init__(self, **kwargs):
        call_docval_func(super(RGBImage, self).__init__, kwargs)


@register_class('RGBAImage', CORE_NAMESPACE)
class RGBAImage(Image):

    @docval(*get_docval(Image.__init__, 'name'),
            {'name': 'data', 'type': ('array_data', 'data'),
             'doc': 'Data of image. Must be 3D where the third dimension has length 4 and represents the RGBA value',
             'shape': (None, None, 4)},
            *get_docval(Image.__init__, 'resolution', 'description'))
    def __init__(self, **kwargs):
        call_docval_func(super(RGBAImage, self).__init__, kwargs)
