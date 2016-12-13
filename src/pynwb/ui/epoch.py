"""
Copyright (c) 2015 Allen Institute, California Institute of Technology, 
New York University School of Medicine, the Howard Hughes Medical 
Institute, University of California, Berkeley, GE, the Kavli Foundation 
and the International Neuroinformatics Coordinating Facility. 
All rights reserved.
    
Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following 
conditions are met:
    
1.  Redistributions of source code must retain the above copyright 
    notice, this list of conditions and the following disclaimer.
    
2.  Redistributions in binary form must reproduce the above copyright 
    notice, this list of conditions and the following disclaimer in 
    the documentation and/or other materials provided with the distribution.
    
3.  Neither the name of the copyright holder nor the names of its 
    contributors may be used to endorse or promote products derived 
    from this software without specific prior written permission.
    
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE 
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN 
ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
POSSIBILITY OF SUCH DAMAGE.
"""
import copy
import numpy as np
import bisect

from ..core import docval, getargs
from .container import Container, properties
from .timeseries import TimeSeries

__std_fields = ('name',
                'description',
                'start_time',
                'stop_time',
                'tags')
@properties(*__std_fields, neurodata_type='Epoch')
class Epoch(Container):
    """ Epoch object
        Epochs represent specific experimental intervals and store
        references to desired time series that overlap with the interval.
        The references to those time series indicate the first
        index in the time series that overlaps with the interval, and the
        duration of that overlap.

        Epochs should be created through NWB.create_epoch(). They should
        not be instantiated directly
    """

    #_neurodata_type = 'Epoch'

    def __init__(self, name, start, stop, description=None, parent=None):
        super(Epoch, self).__init__(parent=parent)
        #**Constructor arguments:**
        #    **name** (text) Name of epoch (must be unique among epochs)
        #    **nwb** NWB object (class)
        #    **start** (float) Start time of epoch, in seconds
        #    **stop** (float) Stop time of epoch, in seconds
        # dict to keep track of which time series are linked to this epoch
        self._timeseries = dict()
        # start and stop time (in seconds)
        self.start_time = start
        self.stop_time = stop
        # name of epoch
        self.name = name
        self.description = description

        self.tags = set()


        # make a copy of the epoch specification
        #self.spec = copy.deepcopy(spec)
        ## reference to nwb 'kernel'
        #self.nwb = nwb
        ## intervals that are for ignoring data (eg, due noise)
        ##self.spec["ignore_intervals"]["_value"] = []
        ## list of tags associated with epoch
        #self.spec["_attributes"]["tags"]["_value"] = []
        #self.spec["_attributes"]["links"]["_value"] = []
        ## go ahead and create epoch folder now
        #if self.name in nwb.file_pointer["epochs"]:
        #    nwb.fatal_error("Epoch %s already exists" % self.name)
        #nwb.file_pointer["epochs"].create_group(self.name)
        #self.serial_num = -1
        #self.finalized = False

    @property
    def timeseries(self):
        return self._timeseries


    def set_description(self, desc):
        """ Convenience function to set the value of the 'description'
            dataset in the epoch

            Arguments:
                *desc* (text) Description of the epoch

            Returns:
                *nothing*
        """
        self.description = desc
        #self.set_value("description", desc)

#    def set_value(self, key, value, **attrs):
#        """Adds an annotating key-value pair (ie, dataset) to the epoch.
#   
#           Arguments:
#               *key* (text) A unique identifier within the TimeSeries
#
#               *value* (any) The value associated with this key
#   
#           Returns:
#               *nothing*
#        """
#        if self.finalized:
#            self.nwb.fatal_error("Added value to epoch after finalization")
#        self.spec[key] = copy.deepcopy(self.spec["[]"])
#        dtype = self.spec[key]["_datatype"]
#        name = "epoch " + self.name
#        self.nwb.set_value_internal(key, value, self.spec, name, dtype, **attrs)

    def add_tag(self, tag):
        """ Append string annotation to epoch. This will be stored in 
            the epoch's 'tags' dataset. Additionally, it will be added
            to a master tag list stored as an attribute on the root
            'epoch/' group. Each epoch can have multiple tags. The root
            epoch keeps a list of unique tags

            Arguments:
                *tag* (text) Name of the tag to add to the epoch

            Returns:
                *nothing*
        """
        self.tags.add(tag)

    # limit intervals to time boundary of epoch, but don't perform 
    #   additional logic (ie, if user supplies overlapping intervals,
    #   let them do so
    def add_ignore_interval(self, start, stop):
        """ Each epoch has a list of intervals that can be flagged to
            be ignored, for example due electrical noise or poor behavior
            of the subject. Intervals are trimmed to fit within epoch
            boundaries, but no further logic is performed (eg, if overlapping
            intervals are specified, those overlaps will be stored)

            Arguments:
                *start* (float) Start of the interval to ignore

                *stop* (float) End time of the interval

            Returns:
                *nothing*
        """
        if start > self.stop_time or stop < self.start_time:
            return  # non-overlapping
        if start < self.start_time:
            start = self.start_time
        if stop > self.stop_time:
            stop = self.stop_time
        self.spec["ignore_intervals"]["_value"].append([start, stop])

    def add_timeseries(self, timeseries, in_epoch_name=None):
        """ Associates time series with epoch. This will create a link
            to the specified time series within the epoch and will
            calculate its overlaps.

            Arguments:
                *in_epoch_name* (text) Name that time series will use 
                in the epoch (this can be different than the actual 
                time series name)

                *timeseries* (text or TimeSeries object) 
                Full hdf5 path to time series that's being added, 
                or the TimeSeries object itself

            Returns:
                *nothing*
        """
        name = in_epoch_name if in_epoch_name else timeseries.name
        self._timeseries[name] = EpochTimeSeries(timeseries, 
                                                self.start_time,
                                                self.stop_time,
                                                name=name,
                                                parent=self)
        return self._timeseries[name]

        


#        # store path to timeseries, so can create hard link
#        epoch_ts = {}
#        if isinstance(timeseries, nwbts.TimeSeries):
#            timeseries_path = timeseries.full_path()
#        elif isinstance(timeseries, str):
#            timeseries_path = timeseries
#        else:
#            self.nwb.fatal_error("Don't recognize timeseries parameter as time series or path")
#        if not timeseries_path.startswith('/'):
#            timeseries_path = '/' + timeseries_path
#        epoch_ts["timeseries"] = timeseries_path
#        #print timeseries_path
#        if timeseries_path not in self.nwb.file_pointer:
#            self.nwb.fatal_error("Time series '%s' not found" % timeseries_path)
#        ts = self.nwb.file_pointer[timeseries_path]
#        if "timestamps" in ts:
#            t = ts["timestamps"].value
#        else:
#            n = ts["num_samples"].value
#            t0 = ts["starting_time"].value
#            rate = ts["starting_time"].attrs["rate"]
#            t = t0 + np.arange(n) / rate
#        # if no overlap, don't add to timeseries
#        # look for overlap between epoch and time series
#        i0, i1 = self.__find_ts_overlap(t)
#        if i0 is None:
#            return
#        epoch_ts["start_idx"] = i0
#        epoch_ts["count"] = i1 - i0 + 1
#        self.timeseries_dict[in_epoch_name] = epoch_ts
#        label = "'" + in_epoch_name + "' is '" + timeseries_path + "'"
#        self.spec["_attributes"]["links"]["_value"].append(label)
#        self.spec["_attributes"]["links"]["_value"].sort()  # VALIDATOR

    # internal function
    # Finds the first element in *timestamps* that is >= *epoch_start*
    # and last element that is <= "epoch_stop"

    # Arguments:
    #     *timestamps* (double array) Timestamp array

    # Returns:
    #     *idx_0*, "idx_1" (ints) Index of first and last elements 
    #     in *timestamps* that fall within specified
    #     interval, or None, None if there is no overlap
    #

    #AJT: I am not sure if this is necessary
    #TODO: Ask AIBS developers why they did this

    def __find_ts_overlap(self, timestamps):
        start = self.start_time
        stop = self.stop_time
        # ensure there are non-nan times
        isnan = np.isnan(timestamps)
        if isnan.all(): 
            return None, None   # all values are NaN -- no overlap
        # convert all nans to a numerical value 
        # when searching for start, use -1
        # when searching for end, use stop+1
        timestamps = np.nan_to_num(timestamps)
        t_test = timestamps + isnan * -1 # make nan<0
        # array now nan-friendly. find first index where timestamps >= start
        i0 = np.argmax(t_test >= start)
        # if argmax returns zero then the first timestamp is >= start or 
        #   no timestamps are. find out which is which
        if i0 == 0:
            if t_test[0] < start:
                return None, None # no timestamps > start
        if t_test[i0] > stop:
            return None, None # timestamps only before start and after stop
        # if we reached here then some or all timestamps are after start
        # search for first after end, adjusting compare array so nan>stop
        t_test = timestamps + isnan * (stop+1)
        # start looking after i0 -- no point looking before, plus if we
        #   do look before and NaNs are present, it screws up the search
        i1 = np.argmin((t_test <= stop)[i0:])
        # if i1 is 0, either all timestamps are <= stop, or all > stop
        if i1 == 0:
            if t_test[0] > stop:
                return None, None # no timestamps < stop
            i1 = len(timestamps) - 1
        else:
            i1 = i0 + i1 - 1 # i1 is the first value > stop. fix that
        # make sure adjusted i1 value is non-nan
        while isnan[i1]:
            i1 = i1 - 1
            assert i1 >= 0
        try:    # error checking 
            assert i0 <= i1
            assert not np.isnan(timestamps[i0])
            assert not np.isnan(timestamps[i1])
            assert timestamps[i0] >= start and timestamps[i0] <= stop
            assert timestamps[i1] >= start and timestamps[i1] <= stop
            return i0, i1
        except AssertionError:
            print("-------------------" + self.name)
            print("epoch: %f, %f" % (start, stop))
            print("time: %f, %f" % (timestamps[0], timestamps[-1]))
            print("idx 0: %d\tt:%f" % (i0, timestamps[i0]))
            print("idx 1: %d\tt:%f" % (i1, timestamps[i1]))
            assert False, "Internal error"

    def finalize(self):
        """ Finish epoch entry and write data to the file

            Arguments:
                *none*

            Returns:
                *nothing*
        """
        if self.finalized:
            return
        # start and stop time stored outside of spec 
        # put them in for writing
        self.spec["start_time"]["_value"] = self.start_time
        self.spec["stop_time"]["_value"] = self.stop_time
        # write epoch entry
        fp = self.nwb.file_pointer
        epoch = fp["epochs"][self.name]
        # manually create time series references
        for k in list(self.timeseries_dict.keys()):
            ts = self.timeseries_dict[k]
            if k in epoch:
                self.nwb.fatal_error("HDF5 object %s exists in epoch %s" % (k, self.name))
            ets = epoch.create_group(k)
            src = self.timeseries_dict[k]["timeseries"]
            ets["timeseries"] = fp[src]
            ets.create_dataset("idx_start", data=ts["start_idx"], dtype='i4')
            ets.create_dataset("count", data=ts["count"], dtype='i4')
        # report all tags to kernel so it can keep track of what was used
        self.nwb.add_epoch_tags(self.spec["_attributes"]["tags"]["_value"])
        # write content to file
        grp = self.nwb.file_pointer["epochs/" + self.name]
        self.nwb.write_datasets(grp, "", self.spec)
        #
        from . import nwb as nwblib
        nwblib.register_finalization(self.name, self.serial_num);
        # flag ourself as done
        self.finalized = True


__epoch_timseries_fields = ('name',
                            'count',
                            'idx_start',
                            'timeseries')    
@properties(*__epoch_timseries_fields)
class EpochTimeSeries(Container):
    def __init__(self, ts, start_time, stop_time, name=None, parent=None):
        super(EpochTimeSeries, self).__init__(parent)
        self.name = name if name else ts.name
        self.timeseries = ts
        #TODO: do something to compute count and idx_start from start_time
        # and stop_time
        if ts.starting_time:
            #n = ts.num_samples
            #t0 = ts.starting_time
            #rate = ts.rate
            #timestamps = t0 + np.arange(n) / rate
            #BEGIN: AJTRITT
            #delta = 1.0/rate
            start_idx = int((start_time - ts.starting_time)*ts.rate)
            stop_idx = int((stop_time - ts.starting_time)*ts.rate)
            #END: AJTRITT
        else:
            timestamps = ts.timestamps
            #XXX This assume timestamps are sorted!
            start_idx = bisect.bisect_left(timestamps, start_time)
            stop_idx = bisect.bisect_left(timestamps, stop_time)
            #TODO: check to see if this should be inclusive or exclusive
            # assume exclusive for now - AJT 10/24/16
        self.count = stop_idx - start_idx
        self.idx_start = start_idx
        

    
