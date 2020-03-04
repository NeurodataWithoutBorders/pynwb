import warnings
from collections.abc import Iterable

from hdmf.utils import docval, popargs, call_docval_func, get_docval

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, Image


@register_class('ImageSeries', CORE_NAMESPACE)
class ImageSeries(TimeSeries):
    '''
    General image data that is common between acquisition and stimulus time series.
    The image data can be stored in the HDF5 file or it will be stored as an external image file.
    '''

    __nwbfields__ = ('dimension',
                     'external_file',
                     'starting_frame',
                     'format')

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': ([None] * 3, [None] * 4),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames. '
                    'dimensions: time, x, y [, z]',
             'default': None},
            *get_docval(TimeSeries.__init__, 'unit'),
            {'name': 'format', 'type': str,
             'doc': 'Format of image. Three types: 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.',
             'default': None},
            {'name': 'external_file', 'type': ('array_data', 'data'),
             'doc': 'Path or URL to one or more external file(s). Field only present if format=external. '
                    'Either external_file or data must be specified, but not both.', 'default': None},
            {'name': 'starting_frame', 'type': Iterable,
             'doc': 'Each entry is the frame number in the corresponding external_file variable. '
                    'This serves as an index to what frames each file contains.', 'default': None},
            {'name': 'bits_per_pixel', 'type': int, 'doc': 'DEPRECATED: Number of bits per image pixel',
             'default': None},
            {'name': 'dimension', 'type': Iterable,
             'doc': 'Number of pixels on x, y, (and z) axes.', 'default': None},
            *get_docval(TimeSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description'))
    def __init__(self, **kwargs):
        bits_per_pixel, dimension, external_file, starting_frame, format = popargs(
            'bits_per_pixel', 'dimension', 'external_file', 'starting_frame', 'format', kwargs)
        call_docval_func(super(ImageSeries, self).__init__, kwargs)
        if external_file is None and self.data is None:
            raise ValueError('must supply either external_file or data to ' + self.name)
        self.bits_per_pixel = bits_per_pixel
        self.dimension = dimension
        self.external_file = external_file
        self.starting_frame = starting_frame
        self.format = format

    @property
    def bits_per_pixel(self):
        return self.fields.get('bits_per_pixel')

    @bits_per_pixel.setter
    def bits_per_pixel(self, val):
        if val is not None:
            warnings.warn("bits_per_pixel is no longer used", DeprecationWarning)
            self.fields['bits_per_pixel'] = val


@register_class('IndexSeries', CORE_NAMESPACE)
class IndexSeries(TimeSeries):
    '''
    Stores indices to image frames stored in an ImageSeries. The purpose of the ImageIndexSeries is to allow
    a static image stack to be stored somewhere, and the images in the stack to be referenced out-of-order.
    This can be for the display of individual images, or of movie segments (as a movie is simply a series of
    images). The data field stores the index of the frame in the referenced ImageSeries, and the timestamps
    array indicates when that image was displayed.
    '''

    __nwbfields__ = ('indexed_timeseries',)

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': (None, ),  # required
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            *get_docval(TimeSeries.__init__, 'unit'),
            {'name': 'indexed_timeseries', 'type': TimeSeries,  # required
             'doc': 'HDF5 link to TimeSeries containing images that are indexed.'},
            *get_docval(TimeSeries.__init__, 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description'))
    def __init__(self, **kwargs):
        name, data = popargs('name', 'data', kwargs)
        indexed_timeseries = popargs('indexed_timeseries', kwargs)
        super(IndexSeries, self).__init__(name, data, **kwargs)
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
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),  # required
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            *get_docval(ImageSeries.__init__, 'unit'),
            {'name': 'masked_imageseries', 'type': ImageSeries,  # required
             'doc': 'Link to ImageSeries that mask is applied to.'},
            *get_docval(ImageSeries.__init__, 'format', 'external_file', 'starting_frame', 'bits_per_pixel',
                        'dimension', 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate', 'comments',
                        'description', 'control', 'control_description'))
    def __init__(self, **kwargs):
        name, data = popargs('name', 'data', kwargs)
        masked_imageseries = popargs('masked_imageseries', kwargs)
        super(ImageMaskSeries, self).__init__(name, data, **kwargs)
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

    @docval(*get_docval(ImageSeries.__init__, 'name'),
            {'name': 'data', 'type': ('array_data', 'data'), 'shape': ([None] * 3, [None, None, None, 3]),
             'doc': 'Images presented to subject, either grayscale or RGB'},
            *get_docval(ImageSeries.__init__, 'unit', 'format'),
            {'name': 'distance', 'type': 'float', 'doc': 'Distance from camera/monitor to target/eye.'},  # required
            {'name': 'field_of_view', 'type': ('array_data', 'data', 'TimeSeries'), 'shape': ((2, ), (3, )),  # required
             'doc': 'Width, height and depth of image, or imaged area (meters).'},
            {'name': 'orientation', 'type': str,  # required
             'doc': 'Description of image relative to some reference frame (e.g., which way is up). '
                    'Must also specify frame of reference.'},
            *get_docval(ImageSeries.__init__, 'external_file', 'starting_frame', 'bits_per_pixel',
                        'dimension', 'resolution', 'conversion', 'timestamps', 'starting_time', 'rate', 'comments',
                        'description', 'control', 'control_description'))
    def __init__(self, **kwargs):
        name, data, = popargs('name', 'data', kwargs)
        distance, field_of_view, orientation = popargs('distance', 'field_of_view', 'orientation', kwargs)
        super(OpticalSeries, self).__init__(name, data, **kwargs)
        self.distance = distance
        self.field_of_view = field_of_view
        self.orientation = orientation


@register_class('GrayscaleImage', CORE_NAMESPACE)
class GrayscaleImage(Image):

    @docval(*get_docval(Image.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'data of image',  # required
             'shape': (None, None)},
            *get_docval(Image.__init__, 'resolution', 'description'))
    def __init__(self, **kwargs):
        call_docval_func(super(GrayscaleImage, self).__init__, kwargs)


@register_class('RGBImage', CORE_NAMESPACE)
class RGBImage(Image):

    @docval(*get_docval(Image.__init__, 'name'),
            {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'data of image',  # required
             'shape': (None, None, 3)},
            *get_docval(Image.__init__, 'resolution', 'description'))
    def __init__(self, **kwargs):
        call_docval_func(super(RGBImage, self).__init__, kwargs)


@register_class('RGBAImage', CORE_NAMESPACE)
class RGBAImage(Image):

    @docval(*get_docval(Image.__init__, 'name'),
            {'name': 'data', 'type': ('array_data', 'data'), 'doc': 'data of image',  # required
             'shape': (None, None, 4)},
            *get_docval(Image.__init__, 'resolution', 'description'))
    def __init__(self, **kwargs):
        call_docval_func(super(RGBAImage, self).__init__, kwargs)
