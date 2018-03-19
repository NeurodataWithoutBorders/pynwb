import numpy as np
from collections import Iterable

from .form.utils import docval, popargs, call_docval_func

from . import register_class, CORE_NAMESPACE
from .base import TimeSeries, _default_resolution, _default_conversion


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
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames',
             'default': None},
            {'name': 'unit', 'type': str,
             'doc': 'The base unit of measurement (should be SI unit)', 'default': 'None'},
            {'name': 'format', 'type': str,
             'doc': 'Format of image. Three types: 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.',
             'default': None},
            {'name': 'external_file', 'type': ('array_data', 'data'),
             'doc': 'Path or URL to one or more external file(s). Field only present if format=external. \
             Either external_file or data must be specified, but not both.', 'default': None},
            {'name': 'starting_frame', 'type': Iterable,
             'doc': 'Each entry is the frame number in the corresponding external_file variable. \
             This serves as an index to what frames each file contains.', 'default': None},
            {'name': 'bits_per_pixel', 'type': int, 'doc': 'Number of bit per image pixel', 'default': None},
            {'name': 'dimension', 'type': Iterable,
             'doc': 'Number of pixels on x, y, (and z) axes.', 'default': [np.nan]},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},
            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default':  'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default':  'no description'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        bits_per_pixel, dimension, external_file, starting_frame, format = popargs(
            'bits_per_pixel', 'dimension', 'external_file', 'starting_frame', 'format', kwargs)
        call_docval_func(super(ImageSeries, self).__init__, kwargs)
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

    __nwbfields__ = ('indexed_timeseries',)

    _ancestry = "TimeSeries,IndexSeries"
    _help = "A sequence that is generated from an existing image stack. Frames can be presented in \
    an arbitrary order. The data[] field stores frame number in reference stack."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'indexed_timeseries', 'type': TimeSeries,
             'doc': 'HDF5 link to TimeSeries containing images that are indexed.'},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
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
        name, source, data, unit = popargs('name', 'source', 'data', 'unit', kwargs)
        indexed_timeseries = popargs('indexed_timeseries', kwargs)
        super(IndexSeries, self).__init__(name, source, data, unit, **kwargs)
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

    _ancestry = "TimeSeries,ImageSeries,ImageMaskSeries"
    _help = "An alpha mask that is applied to a presented visual stimulus."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},
            {'name': 'masked_imageseries', 'type': ImageSeries,
             'doc': 'Link to ImageSeries that mask is applied to.'},
            {'name': 'format', 'type': str,
             'doc': 'Format of image. Three types: 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.'},
            {'name': 'external_file', 'type': Iterable,
             'doc': 'Path or URL to one or more external file(s). Field only present if format=external. \
             Either external_file or data must be specified, but not both.', 'default': None},
            {'name': 'starting_frame', 'type': Iterable,
             'doc': 'Each entry is the frame number in the corresponding external_file variable. \
             This serves as an index to what frames each file contains.', 'default': None},
            {'name': 'bits_per_pixel', 'type': int,
             'doc': 'Number of bit per image pixel', 'default': None},
            {'name': 'dimension', 'type': Iterable,
             'doc': 'Number of pixels on x, y, (and z) axes.', 'default': [np.nan]},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},
            {'name': 'timestamps', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},
            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default': 'no comments'},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset',
             'default': 'no description'},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer',
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None})
    def __init__(self, **kwargs):
        name, source, data, unit, external_file, starting_frame, format = popargs(
            'name', 'source', 'data', 'unit', 'external_file', 'starting_frame', 'format', kwargs)
        masked_imageseries = popargs('masked_imageseries', kwargs)
        super(ImageMaskSeries, self).__init__(name=name, source=source,
                                              data=data, unit=unit,
                                              external_file=external_file,
                                              starting_frame=starting_frame, format=format, **kwargs)
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
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},
            {'name': 'format', 'type': str,
             'doc': 'Format of image. Three types: 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.'},
            {'name': 'distance', 'type': float, 'doc': 'Distance from camera/monitor to target/eye.'},
            {'name': 'field_of_view', 'type': (list, np.ndarray, 'TimeSeries'),
             'doc': 'Width, height and depth of image, or imaged area (meters).'},
            {'name': 'orientation', 'type': str,
             'doc': 'Description of image relative to some reference frame (e.g., which way is up). \
             Must also specify frame of reference.'},
            {'name': 'external_file', 'type': Iterable,
             'doc': 'Path or URL to one or more external file(s). Field only present if format=external. \
             Either external_file or data must be specified, but not both.', 'default': None},
            {'name': 'starting_frame', 'type': Iterable,
             'doc': 'Each entry is the frame number in the corresponding external_file variable. \
             This serves as an index to what frames each file contains.', 'default': None},
            {'name': 'bits_per_pixel', 'type': int, 'doc': 'Number of bit per image pixel', 'default': None},
            {'name': 'dimension', 'type': Iterable,
             'doc': 'Number of pixels on x, y, (and z) axes.', 'default': [np.nan]},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
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
        name, source, data, unit, external_file, starting_frame, format = popargs(
            'name', 'source', 'data', 'unit', 'external_file', 'starting_frame', 'format', kwargs)
        distance, field_of_view, orientation = popargs('distance', 'field_of_view', 'orientation', kwargs)
        super(OpticalSeries, self).__init__(name=name, source=source, data=data, unit=unit,
                                            external_file=external_file, starting_frame=starting_frame,
                                            format=format, **kwargs)
        self.distance = distance
        self.field_of_view = field_of_view
        self.orientation = orientation
