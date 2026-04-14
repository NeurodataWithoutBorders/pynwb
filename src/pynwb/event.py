from hdmf.common import DynamicTable, VectorData
from hdmf.utils import docval, get_docval, AllowPositional

from . import register_class, CORE_NAMESPACE

__all__ = [
    'TimestampVectorData',
    'DurationVectorData',
    'EventsTable',
]


@register_class('TimestampVectorData', CORE_NAMESPACE)
class TimestampVectorData(VectorData):
    """
    A 1-dimensional VectorData that stores timestamps in seconds from the session start time.
    """

    @docval(
        {'name': 'name', 'type': str, 'doc': 'Name of this TimestampVectorData'},
        {'name': 'description', 'type': str, 'doc': 'Description of this TimestampVectorData'},
        *get_docval(VectorData.__init__, 'data'),
        {'name': 'resolution', 'type': float,
         'doc': ('The smallest possible difference between two timestamps. Usually 1 divided by the '
                 'sampling rate for timestamps of the data acquisition system.'),
         'default': None},
        allow_positional=AllowPositional.ERROR,
    )
    def __init__(self, **kwargs):
        resolution = kwargs.pop('resolution', None)
        super().__init__(**kwargs)
        self.resolution = resolution

    @property
    def unit(self):
        """The unit of measurement for the timestamps, fixed to 'seconds'."""
        return 'seconds'


@register_class('DurationVectorData', CORE_NAMESPACE)
class DurationVectorData(VectorData):
    """
    A 1-dimensional VectorData that stores durations in seconds.
    """

    @docval(
        {'name': 'name', 'type': str, 'doc': 'Name of this DurationVectorData'},
        {'name': 'description', 'type': str, 'doc': 'Description of this DurationVectorData'},
        *get_docval(VectorData.__init__, 'data'),
        {'name': 'resolution', 'type': float,
         'doc': ('The smallest possible difference between two durations. Usually 1 divided by the '
                 'sampling rate for the timing of the data acquisition system.'),
         'default': None},
        allow_positional=AllowPositional.ERROR,
    )
    def __init__(self, **kwargs):
        resolution = kwargs.pop('resolution', None)
        super().__init__(**kwargs)
        self.resolution = resolution

    @property
    def unit(self):
        """The unit of measurement for the durations, fixed to 'seconds'."""
        return 'seconds'


@register_class('EventsTable', CORE_NAMESPACE)
class EventsTable(DynamicTable):
    """
    A column-based table to store information about events (event instances), one
    event per row. Additional columns may be added to store metadata about each event,
    such as the duration of the event.
    """

    __columns__ = (
        {'name': 'timestamp', 'description': 'The time that each event occurred, in seconds, '
         'from the session start time.', 'required': True, 'class': TimestampVectorData},
        {'name': 'duration', 'description': 'The duration of each event, in seconds. '
         'A value of NaN can be used for events without a duration.', 'class': DurationVectorData},
        {'name': 'annotation', 'description': 'User annotations about events.'},
    )

    @docval(
        {'name': 'name', 'type': str, 'doc': 'Name of this EventsTable'},
        {'name': 'description', 'type': str,
         'doc': ('A description of the events stored in the table, including information about '
                 'how the event times were computed.')},
        *get_docval(DynamicTable.__init__, 'id', 'columns', 'colnames', 'target_tables', 'meanings_tables'),
        allow_positional=AllowPositional.ERROR,
    )
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @docval(
        {'name': 'timestamp', 'type': float,
         'doc': 'The time that the event occurred, in seconds, from the session start time.'},
        {'name': 'duration', 'type': float,
         'doc': 'The duration of the event, in seconds. Use NaN for events without a duration.',
         'default': None},
        {'name': 'annotation', 'type': str, 'doc': 'User annotation about the event.',
         'default': None},
        allow_extra=True,
    )
    def add_event(self, **kwargs):
        """Add an event to the table."""
        return super().add_row(**kwargs)
