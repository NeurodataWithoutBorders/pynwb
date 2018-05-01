from collections import Iterable

from .form.utils import docval, popargs

from . import register_class, CORE_NAMESPACE
from .core import NWBContainer, MultiContainerInterface
from .misc import IntervalSeries
from .base import TimeSeries, _default_conversion, _default_resolution


@register_class('SpatialSeries', CORE_NAMESPACE)
class SpatialSeries(TimeSeries):
    """
    Direction, e.g., of gaze or travel, or position. The TimeSeries::data field is a 2D array storing
    position or direction relative to some reference frame. Array structure: [num measurements]
    [num dimensions]. Each SpatialSeries has a text dataset reference_frame that indicates the
    zero-position, or the zero-axes for direction. For example, if representing gaze direction,
    "straight-ahead" might be a specific pixel on the monitor, or some other point in space. For
    position data, the 0,0 point might be the top-left corner of an enclosure, as viewed from the
    tracking camera. The unit of data will indicate how to interpret SpatialSeries values.
    """

    __nwbfields__ = ('reference_frame',)

    _ancestry = "TimeSeries,SpatialSeries"

    _help = "Stores points in space over time. The data[] array structure is [num samples][num spatial dimensions]"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this SpatialSeries dataset'},
            {'name': 'source', 'type': str,
             'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                     'contained here. It can also be the name of a device, for stimulus or '
                     'acquisition data')},
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'reference_frame', 'type': str, 'doc': 'description defining what the zero-position is'},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element by to conver to meters',
             'default': _default_conversion},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'timestamps', 'type': ('array_data', 'data', 'TimeSeries'),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default': 'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'parent', 'type': NWBContainer,
             'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
            {'name': 'control', 'type': Iterable,
             'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable,
             'doc': 'Description of each control value', 'default': None},
            )
    def __init__(self, **kwargs):
        """
        Create a SpatialSeries TimeSeries dataset
        """
        name, source, data, reference_frame = popargs('name', 'source', 'data', 'reference_frame', kwargs)
        super(SpatialSeries, self).__init__(name, source, data, 'meters', **kwargs)
        self.reference_frame = reference_frame


@register_class('BehavioralEpochs', CORE_NAMESPACE)
class BehavioralEpochs(MultiContainerInterface):
    """
    TimeSeries for storing behavoioral epochs. The objective of this and the other two Behavioral
    interfaces (e.g. BehavioralEvents and BehavioralTimeSeries) is to provide generic hooks for
    software tools/scripts. This allows a tool/script to take the output one specific interface (e.g.,
    UnitTimes) and plot that data relative to another data modality (e.g., behavioral events) without
    having to define all possible modalities in advance. Declaring one of these interfaces means that
    one or more TimeSeries of the specified type is published. These TimeSeries should reside in a
    group having the same name as the interface. For example, if a BehavioralTimeSeries interface
    is declared, the module will have one or more TimeSeries defined in the module sub-group
    "BehavioralTimeSeries". BehavioralEpochs should use IntervalSeries. BehavioralEvents is used
    for irregular events. BehavioralTimeSeries is for continuous data.
    """

    __clsconf__ = {
        'add': 'add_interval_series',
        'get': 'get_interval_series',
        'create': 'create_interval_series',
        'type': IntervalSeries,
        'attr': 'interval_series'
    }


@register_class('BehavioralEvents', CORE_NAMESPACE)
class BehavioralEvents(MultiContainerInterface):
    """
    TimeSeries for storing behavioral events. See description of BehavioralEpochs for more details.
    """

    _help = "General container for storing event series."

    __clsconf__ = {
        'add': 'add_timeseries',
        'get': 'get_timeseries',
        'create': 'create_timeseries',
        'type': TimeSeries,
        'attr': 'time_series'
    }


@register_class('BehavioralTimeSeries', CORE_NAMESPACE)
class BehavioralTimeSeries(MultiContainerInterface):
    """
    TimeSeries for storing Behavoioral time series data. See description of BehavioralEpochs for
    more details.
    """

    _help = "General container for storing continuously sampled behavioral data"

    __clsconf__ = {
        'add': 'add_timeseries',
        'get': 'get_timeseries',
        'create': 'create_timeseries',
        'type': TimeSeries,
        'attr': 'time_series'
    }


@register_class('PupilTracking', CORE_NAMESPACE)
class PupilTracking(MultiContainerInterface):
    """
    Eye-tracking data, representing pupil size.
    """

    __clsconf__ = {
        'add': 'add_timeseries',
        'get': 'get_timeseries',
        'create': 'create_timeseries',
        'type': TimeSeries,
        'attr': 'time_series'
    }


@register_class('EyeTracking', CORE_NAMESPACE)
class EyeTracking(MultiContainerInterface):
    """
    Eye-tracking data, representing direction of gaze.
    """

    __clsconf__ = {
        'add': 'add_spatial_series',
        'get': 'get_spatial_series',
        'create': 'create_spatial_series',
        'type': SpatialSeries,
        'attr': 'spatial_series'
    }

    _help = "Eye-tracking data, representing direction of gaze"


@register_class('CompassDirection', CORE_NAMESPACE)
class CompassDirection(MultiContainerInterface):
    """
    With a CompassDirection interface, a module publishes a SpatialSeries object representing a
    floating point value for theta. The SpatialSeries::reference_frame field should indicate what
    direction corresponds to 0 and which is the direction of rotation (this should be clockwise). The
    si_unit for the SpatialSeries should be radians or degrees.
    """

    __clsconf__ = {
        'add': 'add_spatial_series',
        'get': 'get_spatial_series',
        'create': 'create_spatial_series',
        'type': SpatialSeries,
        'attr': 'spatial_series'
    }

    _help = "Direction as measured radially. Spatial series reference frame \
    should indicate which direction corresponds to zero and what is the direction of positive rotation."


@register_class('Position', CORE_NAMESPACE)
class Position(MultiContainerInterface):
    """
    Position data, whether along the x, x/y or x/y/z axis.
    """

    __clsconf__ = {
        'add': 'add_spatial_series',
        'get': 'get_spatial_series',
        'create': 'create_spatial_series',
        'type': SpatialSeries,
        'attr': 'spatial_series'
    }

    _help = "Position data, whether along the x, xy or xyz axis"
