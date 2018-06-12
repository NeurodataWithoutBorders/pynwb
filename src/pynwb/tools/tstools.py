from ..base import TimeSeries
from ..form.utils import docval, getargs
from copy import copy
import datetime
import numpy as np
from ..form.array import LinSpace, SortedArray

class TimeSeriesHelper(object):
    """
    Helper class designed for interacting with TimeSeries data
    """
    @docval({'name': 'series', 'type': TimeSeries,  'doc': 'The timeseries for which operations should be performed'})
    def __init__(self, **kwargs):
        self.ts = getargs('series', kwargs)


    @docval({'name': 'time', 'type': float, 'doc': 'The time value to mak to an index in the timeseries'},
            {'name': 'match', 'type': str, 'doc': "Find best matching time 'before' or 'after'.", 'default': 'before'},
            returns="This function returns: 1) the integer index and 2) the floating point time value")
    def time_to_index(self, **kwargs):
        """
        Convert a time value to an index for selection in the timeseries.

        The function will always try to return the index of the exact matching timepoint if available.
        If no exact match for the time is found then the function will return:

        * The closest index before the indicated time if match is set to 'before'
        * The closest index after the indicated time if match is set to 'after'
        * None in case the given time is out of range of the time series

        """
        time, match = getargs('time', 'match', kwargs)
        valid_match_vals = ['before', 'after']
        if match not in valid_match_vals:
            raise ValueError("match=%s invalid. Valid values are one of: %s" % (match, str(valid_match_vals)))
        # Find the closest timestamp in our series
        side = 'left' if match != 'after' else 'right'
        try:
            st = self.get_timestamps()
            result_index = st.find_point(time, side)
            result_time = st[result_index]
        except ValueError:
            result_index = None
            result_time = None
        return result_index, result_time

    def get_timestamps(self):
        """Get SortedArray of timestamps"""
        return self.ts.get_timestamps(as_sortedarray=True)

    def get_absolute_timestamps(self, session_start_time=None):
        """
        Get the timestamps as absolute datatime values rather than floating point offsets

        :param session_start_time: The starttime of the session. May be None in case self.ts has been
               assigned to an NWBFile where the session_start_time can be looked up
        """
        # Define internal helper functions
        def stamp_to_abs_time(session_start_time, stamp):

            return np.datetime64(session_start_time +
                                 datetime.timedelta(seconds=int(stamp)) + \
                                 datetime.timedelta(microseconds=(stamp - int(stamp)) * 1e6))

        def generate_timestamps(session_start_time, stamps):
                for stamp in stamps:
                    yield stamp_to_abs_time(session_start_time, stamp)
                return

        # Try to locate the session start time
        if session_start_time is None:
            curr = self
            while hasattr(curr, 'parent',) and curr.parent is not None:
                print(curr)
                curr = curr.parent
            if hasattr(curr, 'session_start_time'):
                session_start_time = curr.session_start_time
            raise ValueError('Could not locate session_start_time.')

        stamps = self.ts.get_timestamps()
        if len(stamps) <= 0:
            raise ValueError("Cannot create timestamps for empty timeseries")

        absolute_starting_time = stamp_to_abs_time(session_start_time, stamps[0])

        if isinstance(stamps, LinSpace):
            step = np.timedelta64(datetime.timedelta(microseconds=self.ts.rate * 1e6))
            return LinSpace(start=absolute_starting_time,
                            step=step,
                            stop=stamp_to_abs_time(session_start_time, stamps[-1]) + step)
        else:
            return SortedArray(np.fromiter(generate_timestamps(session_start_time, stamps)), dtype=datetime)


    @docval({'name': 'name', 'type': str, 'doc': 'Name of the new subset TimeSeries'},
            {'name': 'time_range', 'type': tuple, 'doc': 'Tuple with start and stop time to select', 'default': None},
            {'name': 'time_match', 'type': tuple,
             'doc': 'Tuple indicting for time_range whether start/stop should be matched "before" or "after".' +
                    'Default behavior is ("before", "before"), i.e., start=before and stop=before ' +
                    'similar to Python index slicing [n,m) where we are left-inclusive (n is in) and ' +
                    'right exclusive (i.e., m is outside of the selection).',
             'default': None},
            {'name': 'index_select', 'type': tuple, 'doc': 'Selections to be applied to self.data.', 'default': None},
            returns='New TimeSeries with data and timestamps adjustd by the applied selection')
    def subset_series(self, **kwargs):
        new_name, time_range, time_match, index_select = getargs('name', 'time_range', 'time_match', 'index_select',
                                                                 kwargs)
        # No selection applied
        if time_range is None and index_select is None:
            return self.ts

        # Validate that time_range and index_select are compatible
        if time_range is not None and index_select is not None:
            if index_select[0] is not None and index_select != slice(None):
                raise ValueError("time_range=%s not compatible with selection specified by index_select[0]=%s" %
                                 (str(time_range), str(index_select[0])))
        if time_range is not None:
            if len(time_range) != 2:
                raise ValueError('time_range must have length 2')
            if time_match is not None and len(time_match) != 2:
                raise ValueError('time_match must have length 2')

        # If we only have a time_range select, then create an empty index_select so we can update it
        if index_select is None:
            index_select = [slice(None), ]

        # Convert the time_range selection to an index selection and update index_select and new_starting_time
        if time_range is not None:
            if time_match is None:
                time_match = ['before', 'before']
            start_index, start_time = self.time_to_index(time=time_range[0], match=time_match[0])
            stop_index, stop_time = self.time_to_index(time=time_range[1], match=time_match[1])
            if start_index is None:
                raise ValueError("No valid start time found %s %s" % (str(time_match[0]), str(time_range[0])))
            if stop_index is None:
                raise ValueError("No valid stop time found %s %s" % (str(time_match[1]), str(time_range[1])))
            index_select[0] = slice(start_index,    # start
                                    stop_index+1,   # stop = +1 because we need to include the stop
                                    1               # step = Select all elements in the range
                                    )
            new_starting_time = start_time
        # Apply our selection to the data
        if isinstance(self.ts.data, list):
            new_data = self.ts.data
            for s in index_select:
                new_data = new_data[s]
        else:
            new_data = self.ts.data[index_select]

        # Initialize the new starting and end times
        new_sampling_rate = None
        new_starting_time = None
        new_timestamps = None
        if self.ts.timestamps is not None:
            new_sampling_rate = None
            new_starting_time = None
            new_timestamps = self.ts.timestamps
        else:
            new_timestamps = None
            new_sampling_rate = self.ts.rate
            start_index = 0
            if isinstance(index_select[0], slice):
                start_index = index_select[0].start
            elif isinstance(index_select[0], list) or isinstance(index_select[0], np.ndarray):
                start_index = index_select[0][0]
            elif isinstance(index_select[0], int):
                start_index = index_select[0]
            else:
                raise NotImplementedError("Could not determine new start time from selection %s" % str(index_select[0]))
            new_starting_time = self.ts.starting_time + self.ts.rate * start_index

        new_fields = dict(data=new_data,
                          timestamps=new_timestamps,
                          sampling_rate=new_sampling_rate,
                          starting_time=new_starting_time)
        for k, v in self.ts.fields.items():
            if k not in new_fields:  # ignore fields we have already set explicitly
                new_fields[k] = copy(v)
        return self.ts.__class__(name=new_name, **new_fields)

    def to_pandas(self, session_start_time=None):
        """
        Convert the time series to a pandas DataFrame timeseries

        :param session_start_time: The starttime of the session. May be None in case self.ts has been
               assigned to an NWBFile where the session_start_time can be looked up

        :return: Pandas dataframe with the absolut times as index and the channels as columns
        """
        import pandas as pd

        data = self.ts.data[:]  # Load all data
        if len(data.shape) > 2:
            data = data.reshape((data.shape[0], np.prod(data.shape[1:])))
        df = pd.DataFrame(data)
        df.set_index(pd.DatetimeIndex(self.get_absolute_timestamps(session_start_time=session_start_time)),
                     inplace=True)
        return df

