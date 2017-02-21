from .base import TimeSeries, Interface, _default_resolution, _default_conversion
from .core import docval, getargs, popargs, NWBContainer

import numpy as np
from collections import Iterable


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

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit = popargs('name', 'source', 'data', 'unit', kwargs)
        bits_per_pixel, dimension, external_file, starting_frame, format = popargs('bits_per_pixel', 'dimension', 'external_file', 'starting_frame', 'format', kwargs)
        super(ImageSeries, self).__init__(name, source, data, unit, **kwargs)


class IndexSeries(TimeSeries):
    '''
    '''

    __nwbfields__ = ('index_timeseries',
                     'index_timeseries_path')

    _ancestry = "TimeSeries,IndexSeries"
    _help = "A sequence that is generated from an existing image stack. Frames can be presented in an arbitrary order. The data[] field stores frame number in reference stack."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'index_timeseries', 'type': str, 'doc': 'HDF5 link to TimeSeries containing images that are indexed.'},
            {'name': 'index_timeseries_path', 'type': str, 'doc': 'Path to linked TimerSeries.'},

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
        index_timeseries, index_timeseries_path = popargs('index_timeseries', 'index_timeseries_path', kwargs)
        super(IndexSeries, self).__init__(name, source, data, unit, **kwargs)

class ImageMaskSeries(ImageSeries):
    '''
    '''

    __nwbfields__ = ('masked_imageseries',
                     'masked_imageseries_path')

    _ancestry = "TimeSeries,ImageSeries,ImageMaskSeries"
    _help = ""

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'masked_imageseries', 'type': str, 'doc': 'Link to ImageSeries that mask is applied to.'},
            {'name': 'masked_imageseries_path', 'type': str, 'doc': 'Path to linked ImageSeries.'},

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
        masked_imageseries, masked_imageseries_path = popargs('masked_imageseries', 'masked_imageseries_path', kwargs)
        super(ImageMaskSeries, self).__init__(name, source, data, unit, external_file, starting_frame, format, **kwargs)

class OpticalSeries(ImageSeries):
    '''
    '''

    __nwbfields__ = ('distance',
                     'field_of_view',
                     'orientation')

    _ancestry = "TimeSeries,ImageSeries,OpticalSeries"
    _help = ""

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

class RoiResponseSeries(TimeSeries):
    '''
    '''

    __nwbfields__ = ('roi_names',
                     'segmenttation_interface',
                     'segmenttation_interface_path')

    _ancestry = "TimeSeries,ImageSeries,ImageMaskSeries"
    _help = ""

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'roi_names', 'type': Iterable, 'doc': 'List of ROIs represented, one name for each row of data[].'},
            {'name': 'segmenttation_interface', 'type': str, 'doc': 'Link to ImageSeries that mask is applied to.'},
            {'name': 'segmenttation_interface_path', 'type': str, 'doc': 'Path to linked ImageSeries.'},

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
        roi_names, segmenttation_interface, segmenttation_interface_path = popargs('roi_names', 'segmenttation_interface', 'segmenttation_interface_path', kwargs)
        super(RoiResponseSeries, self).__init__(name, source, data, unit, **kwargs)

