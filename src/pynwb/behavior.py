from hdmf.utils import docval, popargs, get_docval

from . import register_class, CORE_NAMESPACE
from .core import MultiContainerInterface
from .misc import IntervalSeries
from .base import TimeSeries


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

    @docval(*get_docval(TimeSeries.__init__, 'name'),  # required
            {'name': 'data', 'type': ('array_data', 'data', TimeSeries), 'shape': ((None, ), (None, None)),  # required
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'reference_frame', 'type': str,   # required
             'doc': 'description defining what the zero-position is'},
            *get_docval(TimeSeries.__init__, 'conversion', 'resolution', 'timestamps', 'starting_time', 'rate',
                        'comments', 'description', 'control', 'control_description'))
    def __init__(self, **kwargs):
        """
        Create a SpatialSeries TimeSeries dataset
        """
        name, data, reference_frame = popargs('name', 'data', 'reference_frame', kwargs)
        super(SpatialSeries, self).__init__(name, data, 'meters', **kwargs)
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
