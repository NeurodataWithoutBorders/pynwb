from .core import docval, popargs 
from pynwb.misc import IntervalSeries
from .base import TimeSeries, Interface, _default_conversion, _default_resolution

import numpy as np
from collections import Iterable

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

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},

            {'name': 'reference_frame', 'type': str, 'doc': 'description defining what the zero-position is'},

            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},
            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},

            {'name': 'timestamps', 'type': (list, np.ndarray), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            )
    def __init__(self, **kwargs):
        """
        Create a SpatialSeries TimeSeries dataset
        """
        name, source, data, reference_frame = popargs('name', 'source', 'data', 'reference_frame', kwargs)
        super(SpatialSeries, self).__init__(name, source, data, 'meters', **kwargs)
        self.reference_frame = reference_frame

class BehavioralEpochs(Interface):
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

    __nwbfields__ = ('_IntervalSeries',)

    _help = "General container for storing behavorial epochs."

    @docval({'name': 'source', 'type': str, 'doc': 'The source of the data represented in this Module Interface.'},
            {'name': '_IntervalSeries', 'type': IntervalSeries, 'doc': 'IntervalSeries or any subtype.'})
    def __init__(self, **kwargs):
        source, _IntervalSeries = popargs('source', '_IntervalSeries', kwargs)
        super(BehavioralEpochs, self).__init__(source, **kwargs)
        self._IntervalSeries = _IntervalSeries

class BehavioralEvents(Interface):
    """
    TimeSeries for storing behavioral events. See description of BehavioralEpochs for more details.
    """

    __nwbfields__ = ('_TimeSeries',)

    _help = "General container for storing event series."

    @docval({'name': 'source', 'type': str, 'doc': 'The source of the data represented in this Module Interface.'},
            {'name': '_TimeSeries', 'type': TimeSeries, 'doc': 'TimeSeries or any subtype.'})
    def __init__(self, **kwargs):
        source, _TimeSeries = popargs('source', '_TimeSeries', kwargs)
        super(BehavioralEvents, self).__init__(source, **kwargs)
        self._TimeSeries = _TimeSeries

class BehavioralTimeSeries(Interface):
    """
    TimeSeries for storing Behavoioral time series data.See description of BehavioralEpochs for
    more details.
    """

    __nwbfields__ = ('_TimeSeries',)

    _help = ""

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': '_TimeSeries', 'type': TimeSeries, 'doc': '<TimeSeries> or any subtype.'})
    def __init__(self, **kwargs):
        source, _TimeSeries = popargs('source', '_TimeSeries', kwargs)
        super(BehavioralTimeSeries, self).__init__(source, **kwargs)
        self._TimeSeries = _TimeSeries

class PupilTracking(Interface):
    """
    Eye-tracking data, representing pupil size.
    """

    __nwbfields__ = ('_TimeSeries',)

    _help = "Eye-tracking data, representing pupil size"

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': '_TimeSeries', 'type': TimeSeries, 'doc': ''})
    def __init__(self, **kwargs):
        source, _TimeSeries = popargs('source', '_TimeSeries', kwargs)
        super(PupilTracking, self).__init__(source, **kwargs)
        self._TimeSeries = _TimeSeries

class EyeTracking(Interface):
    """
    Eye-tracking data, representing direction of gaze.
    """

    __nwbfields__ = ('_SpatialSeries',)

    _help = ""

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': '_SpatialSeries', 'type': SpatialSeries, 'doc': ''})
    def __init__(self, **kwargs):
        source, _SpatialSeries = popargs('source', '_SpatialSeries', kwargs)
        super(EyeTracking, self).__init__(source, **kwargs)
        self._SpatialSeries =_SpatialSeries

class CompassDirection(Interface):
    """
    With a CompassDirection interface, a module publishes a SpatialSeries object representing a
    floating point value for theta. The SpatialSeries::reference_frame field should indicate what
    direction corresponds to 0 and which is the direction of rotation (this should be clockwise). The
    si_unit for the SpatialSeries should be radians or degrees.
    """

    __nwbfields__ = ('_SpatialSeries',)

    _help = "Direction as measured radially. Spatial series reference frame should indicate which direction corresponds to zero and what is the direction of positive rotation."

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': '_SpatialSeries', 'type': SpatialSeries, 'doc': 'SpatialSeries or any subtype.'})
    def __init__(self, **kwargs):
        source, _SpatialSeries = popargs('source', '_SpatialSeries', kwargs)
        super(CompassDirection, self).__init__(source, **kwargs)
        self._SpatialSeries = _SpatialSeries

class Position(Interface):
    """
    Position data, whether along the x, x/y or x/y/z axis.
    """

    __nwbfields__ = ('_SpatialSeries',)

    _help = "Position data, whether along the x, xy or xyz axis"

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': '_SpatialSeries', 'type': SpatialSeries, 'doc': ''})
    def __init__(self, **kwargs):
        source, _SpatialSeries = popargs('source', '_SpatialSeries', kwargs)
        super(Position, self).__init__(source, **kwargs)
        self._SpatialSeries = _SpatialSeries

class MotionCorrection(Interface):
    """
    An image stack where all frames are shifted (registered) to a common coordinate system, to
    account for movement and drift between frames. Note: each frame at each point in time is
    assumed to be 2-D (has only x & y dimensions).
    """
    __nwbfields__ = ('image_stack',)

    _help = "Image stacks whose frames have been shifted (registered) to account for motion."

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'image_stack', 'type': Iterable, 'doc': ''})
    def __init__(self, **kwargs):
        source, image_stack = popargs('source', 'image_stack', kwargs)
        super(MotionCorrection, self).__init__(source, **kwargs)
        self.image_stack = image_stack

