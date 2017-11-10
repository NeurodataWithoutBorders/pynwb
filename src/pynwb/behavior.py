import numpy as np
from collections import Iterable

from .form.utils import docval, popargs

from . import register_class, CORE_NAMESPACE
from .core import NWBContainer, set_parents
from .misc import IntervalSeries
from .base import TimeSeries, _default_conversion, _default_resolution
from .image import ImageSeries


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
            {'name': 'data', 'type': (list, np.ndarray, Iterable),
             'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'reference_frame', 'type': str, 'doc': 'description defining what the zero-position is'},
            {'name': 'conversion', 'type': float,
             'doc': 'Scalar to multiply each element by to conver to meters',
             'default': _default_conversion},
            {'name': 'resolution', 'type': float,
             'doc': 'The smallest meaningful difference (in specified unit) between values in data',
             'default': _default_resolution},
            {'name': 'timestamps', 'type': (list, np.ndarray, Iterable),
             'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str,
             'doc': 'Human-readable comments about this TimeSeries dataset', 'default': 'no comments'},
            {'name': 'description', 'type': str,
             'doc': 'Description of this TimeSeries dataset', 'default': 'no description'},
            {'name': 'parent', 'type': 'NWBContainer',
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
class BehavioralEpochs(NWBContainer):
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

    __nwbfields__ = ('interval_series',)

    _help = "General container for storing behavorial epochs."

    @docval({'name': 'name', 'type': str,
             'doc': 'The name of this BehavioralEpochs container', 'default': 'BehavioralEpochs'},
            {'name': 'source', 'type': str, 'doc': 'The source of the data represented in this container.'},
            {'name': 'interval_series', 'type': (list, IntervalSeries), 'doc': 'IntervalSeries or any subtype.'})
    def __init__(self, **kwargs):
        source, interval_series = popargs('source', 'interval_series', kwargs)
        super(BehavioralEpochs, self).__init__(source, **kwargs)
        self.interval_series = set_parents(interval_series, self)


@register_class('BehavioralEvents', CORE_NAMESPACE)
class BehavioralEvents(NWBContainer):
    """
    TimeSeries for storing behavioral events. See description of BehavioralEpochs for more details.
    """

    __nwbfields__ = ('time_series',)

    _help = "General container for storing event series."

    @docval({'name': 'name', 'type': str,
             'doc': 'The name of this BehavioralEvents container', 'default': 'BehavioralEvents'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'time_series', 'type': TimeSeries, 'doc': 'TimeSeries or any subtype.'})
    def __init__(self, **kwargs):
        source, time_series = popargs('source', 'time_series', kwargs)
        super(BehavioralEvents, self).__init__(source, **kwargs)
        self.time_series = time_series


@register_class('BehavioralTimeSeries', CORE_NAMESPACE)
class BehavioralTimeSeries(NWBContainer):
    """
    TimeSeries for storing Behavoioral time series data. See description of BehavioralEpochs for
    more details.
    """

    __nwbfields__ = ('time_series',)

    _help = ""

    @docval({'name': 'name', 'type': str,
             'doc': 'The name of this BehavioralTimeSeries', 'default': 'BehavioralTimeSeries'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'time_series', 'type': TimeSeries, 'doc': '<TimeSeries> or any subtype.'})
    def __init__(self, **kwargs):
        source, time_series = popargs('source', 'time_series', kwargs)
        super(BehavioralTimeSeries, self).__init__(source, **kwargs)
        self.time_series = time_series


@register_class('PupilTracking', CORE_NAMESPACE)
class PupilTracking(NWBContainer):
    """
    Eye-tracking data, representing pupil size.
    """

    __nwbfields__ = ('time_series',)

    _help = "Eye-tracking data, representing pupil size"

    @docval({'name': 'name', 'type': str,
             'doc': 'The name of this PupilTracking container', 'default': 'PupilTracking'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'time_series', 'type': TimeSeries, 'doc': ''})
    def __init__(self, **kwargs):
        source, time_series = popargs('source', 'time_series', kwargs)
        super(PupilTracking, self).__init__(source, **kwargs)
        self.time_series = time_series


@register_class('EyeTracking', CORE_NAMESPACE)
class EyeTracking(NWBContainer):
    """
    Eye-tracking data, representing direction of gaze.
    """

    __nwbfields__ = ('spatial_series',)

    _help = ""

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this EyeTracking container', 'default': 'EyeTracking'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'spatial_series', 'type': (list, SpatialSeries), 'doc': ''})
    def __init__(self, **kwargs):
        source, spatial_series = popargs('source', 'spatial_series', kwargs)
        super(EyeTracking, self).__init__(source, **kwargs)
        self.spatial_series = set_parents(spatial_series, self)


@register_class('CompassDirection', CORE_NAMESPACE)
class CompassDirection(NWBContainer):
    """
    With a CompassDirection interface, a module publishes a SpatialSeries object representing a
    floating point value for theta. The SpatialSeries::reference_frame field should indicate what
    direction corresponds to 0 and which is the direction of rotation (this should be clockwise). The
    si_unit for the SpatialSeries should be radians or degrees.
    """

    __nwbfields__ = ('spatial_series',)

    _help = "Direction as measured radially. Spatial series reference frame \
    should indicate which direction corresponds to zero and what is the direction of positive rotation."

    @docval({'name': 'name', 'type': str,
            'doc': 'The name of this CompassDirection container', 'default': 'CompassDirection'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'spatial_series', 'type': (list, SpatialSeries), 'doc': 'SpatialSeries or any subtype.'})
    def __init__(self, **kwargs):
        source, spatial_series = popargs('source', 'spatial_series', kwargs)
        super(CompassDirection, self).__init__(source, **kwargs)
        self.spatial_series = set_parents(spatial_series, self)


@register_class('Position', CORE_NAMESPACE)
class Position(NWBContainer):
    """
    Position data, whether along the x, x/y or x/y/z axis.
    """

    __nwbfields__ = ('spatial_series',)

    _help = "Position data, whether along the x, xy or xyz axis"

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this Position container', 'default': 'Position'},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'spatial_series', 'type': (list, SpatialSeries), 'doc': ''})
    def __init__(self, **kwargs):
        source, spatial_series = popargs('source', 'spatial_series', kwargs)
        super(Position, self).__init__(source, **kwargs)
        self.spatial_series = set_parents(spatial_series, self)


@register_class('CorrectedImageStack', CORE_NAMESPACE)
class CorrectedImageStack(NWBContainer):
    """
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
class MotionCorrection(NWBContainer):
    """
    An image stack where all frames are shifted (registered) to a common coordinate system, to
    account for movement and drift between frames. Note: each frame at each point in time is
    assumed to be 2-D (has only x & y dimensions).
    """

    __nwbfields__ = ('corrected_image_stacks',)

    _help = "Image stacks whose frames have been shifted (registered) to account for motion."

    @docval({'name': 'name', 'type': str,
             'doc': 'The name of this MotionCorrection container', 'default': 'MotionCorrection '},
            {'name': 'source', 'type': str, 'doc': 'the source of the data'},
            {'name': 'corrected_image_stacks', 'type': (list, CorrectedImageStack),
             'doc': 'the corrected image stack in this Motion Correction analysis'})
    def __init__(self, **kwargs):
        source, corrected_image_stacks = popargs('source', 'corrected_image_stacks', kwargs)

        if isinstance(corrected_image_stacks, CorrectedImageStack):
            corrected_image_stacks = [corrected_image_stacks]

        super(MotionCorrection, self).__init__(source, **kwargs)
        self.corrected_image_stacks = corrected_image_stacks
