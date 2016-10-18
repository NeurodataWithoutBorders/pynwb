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
import sys
import traceback
import copy
from . import nwbmo


MOD_ACQUISITION = "acquisition"
MOD_STIMULUS = "stimulus"
MOD_TEMPLATE = "template"
MOD_OTHER = "other"

__modality_location__

class TimeSeries(object):
    """ Standard TimeSeries constructor

        All time series are created by calls to  NWB.create_timeseries(). 
        They should not not be instantiated directly
    """
    _default_conversion = 1.0
    _default_resolution = np.nan
    #def __init__(self, name, modality, spec, nwb):
        ## make a local copy of the specification, one that can be modified
        #self.spec = copy.deepcopy(spec)
        # file handling
        #self.nwb = nwb
        #self.finalized = False
        ## AJTRITT: Move modality into NWB class. 
        ##          NWB class will decide where to store this TimeSeries object
        # # check modality and set path
        # if modality == "acquisition":
        #     self.path = "/acquisition/timeseries/"
        # elif modality == "stimulus":
        #     self.path = "/stimulus/presentation/"
        # elif modality == "template":
        #     self.path = "/stimulus/templates/"
        # elif modality == "other":
        #     self.path = ""
        # else:
        #     m = "Modality must be acquisition, stimulus, template or other"
        #     self.fatal_error(m)
        # if self.path is not None:
        #     full_path = self.path + self.name
        #     if full_path in self.nwb.file_pointer:
        #         self.fatal_error("Group '%s' already exists" % full_path)
        # self.time_tgt_path = None
        # self.data_tgt_path = None
        # self.data_tgt_path_soft = None
        # self.serial_num = -1

    _ancestry = 'TimeSeries'

    def __init__(self, name):
        self._name = name
        self.data_link = set()
        self.timestamps_link = set()
        self._data = None
        self._timeseries = None

    @property
    def name(self):
        return self._name

    @property
    def ancestry(self):
        return self._ancestry

    @property
    def data(self):
        if isinstance(self._data, TimeSeries):
            return self._data.data
        else:
            return self._data

    @property
    def timestamps(self):
        if isinstance(self._timestamps, TimeSeries):
            return self._timestamps.timestamps
        else:
            return self._timestamps

    # internal function
    def fatal_error(self, msg):
        print("Error: " + msg)
        print("TimeSeries: " + self.name)
        print("Stack trace follows")
        print("-------------------")
        traceback.print_stack()
        sys.exit(1)

    # internal function for changing the name of a time series
    # don't publish this as a user shouldn't be doing it
    def reset_name(self, name):
        self.name = name

    ####################################################################
    # set field values

    # don't allow setting attributes on values, not for now at least
    # it's not legal to add attributes to fields that are in the spec as
    #   there is no way to mark them as custom
    @deprecated
    def set_value(self, key, value, dtype=None):
        """ Set key-value pair, with optional attributes (in dtype)

            Arguments:
                *key* (text) Name of dataset that stores the data

                *value* (any) Data to be stored

                *dtype* (text) h5py datatype that should be used
                for storing the data

            Returns:
                *nothing*
        """
        if self.finalized:
            self.fatal_error("Added value after finalization")
        name = "TimeSeries %s" % self.name
        self.nwb.set_value_internal(key, value, self.spec, name, dtype)

    # internal function used for setting data[] and timestamps[]
    # this method doesn't include necessary logic to manage attributes
    #   and prevent the user from adding custom attributes to
    #   standard fields, or to alter required 'custom' attribute
    @deprecated
    def set_value_with_attributes_internal(self, key, value, dtype, **attrs):
        if self.finalized:
            self.fatal_error("Added value after finalization")
        name = "TimeSeries %s" % self.name
        self.nwb.set_value_internal(key, value, self.spec, name, dtype, **attrs)

    # have special calls for those that are common to all time series
    def set_description(self, value):
        """ Convenience function to set the description field of the
            *TimeSeries*
        """
        self.description = value

    def set_comments(self, value):
        """ Convenience function to set the comments field of the
            *TimeSeries*
        """
        self.comments = comments

    # for backward compatibility to screwy scripts, and to be nice
    #   in event of typo
    def set_comment(self, value):
        self.set_comments(value)

    def set_source(self, value):
        """ Convenience function to set the source field of the
            *TimeSeries*
        """
        self.source = value

    #TODO: add this functionality to validation code
    @deprecated
    def ignore_time(self):
        """ In some cases (eg, template stimuli) there is no time 
            data available. Rather than store invalid data, it's better
            to explicitly avoid setting the time field

            Arguments:
                *none*

            Returns:
                *nothing*
        """
        if self.finalized:
            self.fatal_error("Changed timeseries after finalization")
        # downgrade required status so file will generate w/o
        self.spec["timestamps"]["_include"] = "standard"
        self.spec["starting_time"]["_include"] = "standard"
        self.spec["num_samples"]["_include"] = "standard"

    # if default value used, value taken from specification file
    def set_data(self, data, unit, conversion=None, resolution=None, dtype=None):
        '''Defines the data stored in the TimeSeries. Type of data 
           depends on which class of TimeSeries is being used

           Arguments:
               *data* (user-defined) Array of data samples stored in time series

               *unit* (text) Base SI unit for data[] (eg, Amps, Volts)

               *conversion* (float) Multiplier necessary to convert elements in data[] to specified unit

               *resolution* (float) Minimum meaningful distance between elements in data[] (e.g., the +/- range, quantal step size between values, etc). If unknown, store NaN
   
           Returns:
               *nothing*
        '''
        self.unit = unit
        self.conversion = conversion if conversion else _default_conversion,
        self.resolution = resolution if resolution else _default_resolution,

        attrs = {}
        if unit is not None:
            attrs["unit"] = str(unit)
        if conversion is not None:
            attrs["conversion"] = float(conversion)
        if resolution is not None:
            attrs["resolution"] = float(resolution)
        self.set_value_with_attributes_internal("data", data, dtype, **attrs)

    def link_data(self, ts):
        '''Links the *data* dataset in this TimeSeries to that
           stored in another TimeSeries. This is useful when multiple time
           series represent the same data.
           This works by making an HDF5 hard link to the data array
           in the sibling time series
   
           Arguments:
               *sibling* (text) Full HDF5 path to TimeSeries containing source data[] array, or a python TimeSeries object
   
           Returns:
               *nothing*
        '''
        target_ts = ts
        while True:
            if isinstance(target_ts.timestamps, TimeSeries):
                target_ts = target_ts.timestamps
                continue
            break
        self.data = ts
        target_ts.data_link.add(self)

    def ignore_data(self):
        """ In some cases (eg, externally stored image files) there is no 
            data to be stored. Rather than store invalid data, it's better
            to explicitly avoid setting the data field

            Arguments:
                *none*

            Returns:
                *nothing*
        """
        if self.finalized:
            self.fatal_error("Changed timeseries after finalization")
        # downgrade required status so file will generate w/o
        self.spec["data"]["_include"] = "standard"

    ####################################################################
    ####################################################################

    def set_time(self, timearray):
        ''' Store timestamps for the time series. 
   
           Arguments:
               *timearray* (double array) Timestamps for each element in *data*
   
           Returns:
               *nothing*
        '''
        self.timestamps = timearray
        self.interval = 1
        self.unit = "Seconds"
        
        # t_interval should have default value set to 1 in spec file
        self.set_value("timestamps", timearray)

    def set_time_by_rate(self, time_zero, rate):
        '''Store time by start time and sampling rate only
   
           Arguments:
               *time_zero* (double) Time of data[] start. For template stimuli, this should be zero
               *rate* (float) Cycles per second (Hz)
   
           Returns:
               *nothing*
        '''
        self.starting_time = time_zero
        self.rate = rate
        self.unit = "Seconds"

    # takes the path to the sibling time series to create a hard link
    #   to its timestamp array
    def link_time(self, ts):
        '''Links the *timestamps* dataset in this TimeSeries to that
           stored in another TimeSeries. This is useful when multiple time
           series have data that is recorded on the same clock.
           This works by making an HDF5 hard link to the timestamps array
           in the sibling time series
   
           Arguments:
               *sibling* (text) Full HDF5 path to TimeSeries containing source timestamps array, or a python TimeSeries object
   
           Returns:
               *nothing*
        '''
        target_ts = ts
        while True:
            if isinstance(target_ts.timestamps, TimeSeries):
                target_ts = target_ts.timestamps
                continue
            break
        self.timestamps = target_ts
        target_ts.timestamps_link.add(self)
#
#        if self.finalized:
#            self.fatal_error("Added value after finalization")
#        # it's possible that this TimeSeries path isn't set at the 
#        #   time of the link (eg, if the TimeSeries is part of a
#        #   module) so we can't register the path w/ the kernel yet.
#        #   store link info for finalization, when path is known
#        self.time_tgt_path = self.create_hardlink("timestamps", sibling)
#
    def build_hdf5(self):
        builder = GroupBuilder()
        builder.set_attribute('description', self.description)
        builder.set_attribute('source', self.source)
        builder.set_attribute('comments', self.comments)
        if isinstance(self._data, TimeSeries):
            if self._data.file_name != self.file_name:
                #TODO: figure out how to compute dataset_path
                builder.add_external_link('data', self._data.file_name, dataset_path)
            else:
                #TODO: figure out how to compute dataset_path
                builder.add_soft_link('data', dataset_path)
        else:
            data_attrs = {
                "unit": unit, 
                "conversion": conversion if conversion else _default_conversion,
                "resolution": resolution if resolution else _default_resolution,
            }
            builder.add_dataset("data", self._data, attributes=data_attrs)
        
        if self.starting_time:
            builder.add_dataset("starting_time",
                                        self.starting_time, 
                                        attributes={"rate": self.rate, 
                                                    "unit": "Seconds"})
        else:
            if isinstance(self._timestamps, TimeSeries):
                if self._timestamps.file_name != self.file_name:
                    #TODO: figure out how to compute timestamps_path
                    builder.add_external_link('data', self._data.file_name, timestamps_path)
                else:
                    #TODO: figure out how to compute timestamps_path
                    builder.add_soft_link('timestamps', timestamps_path)
            else:
                ts_attrs = {"interval": 1, "unit": "Seconds"}
                builder.add_dataset("timestamps", self._timestamps, attributes=ts_attrs)
        return builder
        
#        if self.finalized:
#            self.fatal_error("Added value after finalization")
#        # it's possible that this TimeSeries path isn't set at the 
#        #   time of the link (eg, if the TimeSeries is part of a
#        #   module) so we can't register the path w/ the kernel yet.
#        #   store link info for finalization, when path is known
#        self.data_tgt_path = self.create_hardlink("data", sibling)
#
#    @deprecated
#    def set_data_as_remote_link(self, file_path, dataset_path):
#        '''Links the *data* dataset in this TimeSeries to data stored
#           in an external file, using and HDF5 soft-link.
#           The dataset in the external file must contain attributes required 
#           for the TimeSeries::data[] element.
#   
#           Arguments:
#               *file_path* (text) File-system path to remote HDF5 file
#
#               *dataset_path* (text) Full path within remote HDF5 file to dataset
#   
#           Returns:
#               *nothing*
#        '''
#
#        if self.finalized:
#            self.fatal_error("Added value after finalization")
#        self.create_softlink("data", file_path, dataset_path)
#        # it's possible that this TimeSeries path isn't set at the 
#        #   time of the link (eg, if the TimeSeries is part of a
#        #   module) so we can't register the path w/ the kernel yet.
#        #   store link info for finalization, when path is known
#        self.data_tgt_path_soft = file_path + "://" + dataset_path
#        #self.nwb.record_timeseries_data_soft_link(self.full_path(), file_path+"://"+dataset_path)
#        extern_fields = self.spec["_attributes"]["extern_fields"]
#        if "_value" not in extern_fields:
#            extern_fields["_value"] = []
#        extern_fields["_value"].append("data")
#
#
#    # internal function
#    # creates link to similarly named field between two groups
#    @deprecated
#    def create_hardlink(self, field, target):
#        # type safety -- make sure sibling is class if not string
#        if self.finalized:
#            self.fatal_error("Added value after finalization")
#        if isinstance(target, str):
#            sib_path = target
#        elif isinstance(target, TimeSeries):
#            sib_path = target.full_path()
#        elif isinstance(target, nwbmo.Module):
#            sib_path = target.full_path()
#        else:
#            self.fatal_error("Unrecognized link-to object. Expected str or TimeSeries, found %s" % type(target))
#        # define link. throw error if value was already set
#        if "_value" in self.spec[field]:
#            self.fatal_error("cannot specify a link after setting value")
#        elif "_value_softlink" in self.spec[field]:
#            self.fatal_error("cannot specify both hard and soft links")
#        self.spec[field]["_value_hardlink"] = sib_path + "/" + field
#        # return path string
#        return sib_path
#
#
#    # internal function
#    # creates link to similarly named field between two groups
#    @deprecated
#    def create_softlink(self, field, file_path, dataset_path):
#        if self.finalized:
#            self.fatal_error("Added value after finalization")
#        if "_value" in self.spec[field]:
#            self.fatal_error("cannot specify a data link after set_data()")
#        elif "_value_hardlink" in self.spec[field]:
#            self.fatal_error("cannot specify both hard and soft links")
#        self.spec[field]["_value_softlink"] = dataset_path
#        self.spec[field]["_value_softlink_file"] = file_path
#

    ####################################################################
    ####################################################################
    # file writing and path management

    @deprecated
    def set_path(self, path):
        """ Sets the path for where the *TimeSeries* is created. This
            is only necessary for *TimeSeries* that were not created
            indicating the common storage location (ie, acquisition,
            stimulus, template) or that were not added to a module
        """
        if self.finalized:
            self.fatal_error("Added value after finalization")
        if path.endswith('/'):
            self.path = path
        else:
            self.path = path + "/"
        full_path = self.path + self.name
        if full_path in self.nwb.file_pointer:
            self.fatal_error("group '%s' already exists" % full_path)

    @deprecated
    def full_path(self):
        """ Returns the HDF5 path to this *TimeSeries*

            Arguments: 
                *none*

            Returns:
                *nothing*
        """
        return self.path + self.name

    @deprecated
    def finalize(self):
        """ Finish the *TimSeries* and write pending changes to disk

            Arguments:
                *none*

            Returns:
                *nothing*
        """
        if self.finalized:
            return
        # verify path is in acceptable location
        # AJTRITT: BEGIN validation
        valid_loc = False   # ever the pessimest
        template = False    
        if self.path.startswith("/acquisition/timeseries"):
            valid_loc = True
        elif self.path.startswith("acquisition/timeseries"):
            valid_loc = True
        elif self.path.startswith("/stimulus/templates"):
            valid_loc = True
            template = True
        elif self.path.startswith("stimulus/templates"):
            valid_loc = True
            template = True
        elif self.path.startswith("/stimulus/presentation"):
            valid_loc = True
        elif self.path.startswith("stimulus/presentation"):
            valid_loc = True
        elif self.path.startswith("/analysis"):
            valid_loc = True
        elif self.path.startswith("analysis"):
            valid_loc = True
        elif self.path.startswith("/processing") and len(self.path) > len("/processing/"):
            valid_loc = True
        elif self.path.startswith("processing") and len(self.path) > len("processing/"):
            valid_loc = True
        if not valid_loc:
            print("Timeseries '%s' is not stored in a correct location" % self.name)
            print("Specified path is '%s'" % self.path)
            print("Possible solutions:")
            print("1) when creating the time series, specify modality='acquisition', ")
            print("   'stimulus' or 'template' and the path will be correctly")
            print("   assigned")
            print("2) add the time series to a processing module")
            print("3) manually assign a valid directory in '/acquisition/',")
            print("   'stimulus', 'processing' or 'analysis' folders")
            self.nwb.fatal_error("Invalid TimeSeries path")
        # AJTRITT: END validation

        valid_loc = False   # ever the pessimest
        from . import nwb as nwblib
        nwblib.register_finalization(self.path + self.name, self.serial_num)
        # tell kernel about link so table of all links can be added to
        #   file at end
        if self.data_tgt_path_soft is not None:
            self.nwb.record_timeseries_data_soft_link(self.full_path(), self.data_tgt_path_soft)
        if self.data_tgt_path is not None:
            self.nwb.record_timeseries_data_link(self.full_path(), self.data_tgt_path)
        if self.time_tgt_path is not None:
            self.nwb.record_timeseries_time_link(self.full_path(), self.time_tgt_path)
        # verify all mandatory fields are present
        # AJTRITT: BEGIN validation
        spec = self.spec
        if template:    # VALIDATOR
            spec["timestamps"]["_include"] = "optional"
            spec["starting_time"]["_include"] = "optional"
        # num_samples can sometimes be calculated automatically. do so
        #   here if that's possible
        if "_value" not in spec["num_samples"]:
            if "_value" in spec["timestamps"]:
                # make tmp short name to avoid passing 80-col limit in editor
                tdat = spec["timestamps"] 
                spec["num_samples"]["_value"] = len(tdat["_value"])
        # document missing standard fields
        err_str = []
        missing_fields = []
        for k in list(spec.keys()):
            if k.startswith('_'):   # check for leading underscore
                continue    # control field -- ignore
            if "_value" in spec[k]:
                continue    # field exists
            if spec[k]["_include"] == "required":
                # value is missing -- see if alternate or link exists
                if "_value_softlink" in spec[k]:
                    continue
                if "_value_hardlink" in spec[k]:
                    continue
                # valid alternative fields include links -- check possibilities
                if "_alternative" in spec[k]:
                    if "_value" in spec[spec[k]["_alternative"]]:
                        continue    # alternative field exists
                    if "_value_hardlink" in spec[spec[k]["_alternative"]]:
                        continue    # alternative field exists
                    if "_value_softlink" in spec[spec[k]["_alternative"]]:
                        continue    # alternative field exists
                miss_str = "Missing field '%s'" % k
                if "_alternative" in spec[k]:
                    miss_str += " (or '%s')" % spec[k]["_alternative"]
                err_str.append(str(miss_str))
            # make a record of missing required fields
            if spec[k]["_include"] == "standard":
                if "_value" not in spec["_attributes"]["missing_fields"]:
                    spec["_attributes"]["missing_fields"]["_value"] = []
                spec["_attributes"]["missing_fields"]["_value"].append(str(k))
                missing_fields.append(str(k))
        # add spec's _description to 'help' field
        # use asserts -- there's a problem w/ the spec if these don't exist
        assert "help" in spec["_attributes"]
        assert "_description" in spec
        spec["_attributes"]["help"]["_value"] = spec["_description"]
        # make sure that mandatory attributes are present
        lspec = []
        lspec.append(spec)
        if "_value" in spec["data"]:
            lspec.append(spec["data"])
        if "_value" in spec["timestamps"]:
            lspec.append(spec["timestamps"])
        if "_value" in spec["starting_time"]:
            lspec.append(spec["starting_time"])
        for i in range(len(lspec)):
            for k in lspec[i]["_attributes"]:
                if lspec[i]["_attributes"][k]["_include"] == "required":
                    if "_value" not in lspec[i]["_attributes"][k]:
                        err_str.append("Missing attribute: " + k)
        # AJTRITT: END validation

        # report missing standard data
        if len(missing_fields) > 0:
            missing_fields.sort()
            spec["_attributes"]["missing_fields"]["_value"].sort()
            print("Warning -- '%s' is missing the following:" % self.full_path())
            for i in range(len(missing_fields)):
                print("\t" + missing_fields[i])
        # report errors for missing mandatory data
        if len(err_str) > 0:
            print("TimeSeries creation error (name=%s; path=%s)" % (self.name, self.full_path()))
            if len(err_str) == 1:
                print("Missing mandatory field:")
            else:
                print("Missing mandatory field(s):")
            for i in range(len(err_str)):
                print("\t" + err_str[i])
            sys.exit(1)
        # TODO check _linkto

        # make sure dataset or group doesn't already exist w/ this name
        if self.full_path() in self.nwb.file_pointer:
            self.fatal_error("HDF5 element %s already exists"%self.full_path())
        # write content to file
        grp = self.nwb.file_pointer.create_group(self.full_path())
        self.nwb.write_datasets(grp, "", spec)

        # allow freeing of memory
        self.spec = None
        # set done flag
        self.finalized = True



class AnnotationSeries(TimeSeries):
    ''' Stores text-based records about the experiment. To use the
        AnnotationSeries, add records individually through 
        add_annotation() and then call finalize(). Alternatively, if 
        all annotations are already stored in a list, use set_data()
        and set_timestamps()

        All time series are created by calls to  NWB.create_timeseries(). 
        They should not not be instantiated directly
    ''' 

    _ancestry = "TimeSeries,AnnotationSeries"
    
    def __init__(self, name, modality, spec, nwb):
        super(AnnotationSeries, self).__init__(name, modality, spec, nwb)

        self.builder.set_attribute("help", "Time-stamped annotations about an experiment")
        self.set_data(list())
        self.set_time(list())
        
        #self.annot_str = []
        #self.annot_time = []

    def add_annotation(self, what, when):
        '''Convennece function to add annotations individually

        Arguments:
            *what* (text) Annotation

            *when* (double) Timestamp for annotation

        Returns:
            *nothing*
        '''
        self.builder['data'].append(str(what))
        self.builder['timestamps'].append(str(what))

        #self.annot_str.append(str(what))
        #self.annot_time.append(float(when))

    def set_data(self, data):
        super().set_data(data, "n/a", conversion=np.nan, resolution=np.nan)

    #def finalize(self):
    #    '''Extends superclass call by pushing annotations onto 
    #    the data[] and timestamps[] fields

    #    Arguments:
    #        *none*

    #    Returns:
    #        *nothing*
    #    '''
    #    if self.finalized:
    #        return
    #    if len(self.annot_str) > 0:
    #        if "_value" in self.spec["data"]:
    #            print("AnnotationSeries error -- can only call set_data() or add_annotation(), not both")
    #            print("AnnotationSeries name: " + self.name)
    #            sys.exit(1)
    #        if "_value" in self.spec["timestamps"]:
    #            print("AnnotationSeries error -- can only call set_time() or add_annotation(), not both")
    #            print("AnnotationSeries name: " + self.name)
    #            sys.exit(1)
    #        self.spec["data"]["_value"] = self.annot_str
    #        self.spec["timestamps"]["_value"] = self.annot_time
    #    super(AnnotationSeries, self).finalize()

class AbstractFeatureSeries(TimeSeries):
    """ Represents the salient features of a data stream. Typically this
        will be used for things like a visual grating stimulus, where
        the bulk of data (each frame sent to the graphics card) is bulky
        and not of high value, while the salient characteristics (eg,
        orientation, spatial frequency, contrast, etc) are what important
        and are what are used for analysis

        All time series are created by calls to  NWB.create_timeseries(). 
        They should not not be instantiated directly
    """

    _ancestry = "TimeSeries,AbstractFeatureSeries"

    def set_features(self, names, units):
        """ Convenience function for setting feature values. Has logic to
            ensure arrays have equal length (ie, sanity check)

            Arguments:
                *names* (text array) Description of abstract features

                *units* (text array) Units for each of the abstract features

            Returns:
                *nothing*
        """
        self.features = names
        self.units = units
        
    def build_hdf5(self):
        builder = super().build_hdf5()
        builder.add_dataset('features', self.features)
        builder.add_dataset('feature_units', self.units)
        return builder
    
        ## sanlty checks
        ## make sure both are arrays, not strings
        #if isinstance(names, str):
        #    names = [ str(names) ]
        #if isinstance(units, str):
        #    units = [ str(units) ]
        ## make sure arrays are of same length
        #if len(names) != len(units):
        #    self.fatal_error("name and unit vectors must have equal length")
        #self.set_value("features", names)
        #self.set_value("feature_units", units)

class ElectricalSeries(TimeSeries):

    _ancestry = "TimeSeries,ElectricalSeries"
    _help = "Stores acquired voltage data from extracellular recordings"

    def __init__(self, name, electrodes=None):
        """ Create a new ElectricalSeries dataset
            
            Arguments:
                *names* (int array) The electrode indices
        """
        super().__init__(name)
        if electrodes:
            self.set_electrodes(electrodes)
    
    def set_data(self, data, conversion=None, resolution=None):
        """
            Arguments:
                *conversion* (float)  Scalar to multiply each datapoint by to
                                      convert to volts

                *resolution* (float)  Scalar to multiply each datapoint by to
                                      convert to volts
        """
        super().set_data(data, "volt", conversion=conversion, resolution=resolution)

    def set_electrodes(self, electrodes):
        """ Specify the electrodes that this corresponds to in the electrode
            map.
            
            Arguments:
                *names* (int array) The electrode indices
        """
        self.electrodes = electrodes
    
    def build_hdf5(self):
        builder = super().build_hdf5()
        builder.add_dataset("electrode_idx", self.electrodes)
        return builder


class SpikeSeries(ElectricalSeries):

    _ancestry = "TimeSeries,ElectricalSeries,SpikeSeries"

    _help = "Snapshots of spike events from data."

    def __init__(self, name, electrodes=None):
        super().__init__(name, electrodes)
        super().set_data(list())
        
    def add_spike(event_data):
        self.builder['data'].append(event_data)
    
class ImageSeries(TimeSeries):
    pass

class ImageMaskSeries(ImageSeries):
    pass

class OpticalSeries(ImageSeries):
    pass

class TwoPhotonSeries(ImageSeries):
    pass

class IndexSeries(TimeSeries):
    pass

class IntervalSeries(TimeSeries):
    pass

class OptogeneticSeries(TimeSeries):
    def set_data(self, data, conversion=None, resolution=None):
        super().set_data(data, "watt", conversion=conversion, resolution=resolution)

class PatchClampSeries(TimeSeries):
    pass

class CurrentClampSeries(PatchClampSeries):
    pass

class IZeroClampSeries(CurrentClampSeries):
    pass

class CurrentClampStimulusSeries(PatchClampSeries):
    pass

class VoltageClampSeries(PatchClampSeries):
    pass

class VoltageClampStimulusSeries(PatchClampSeries):
    pass

class RoiResponseSeries(TimeSeries):
    pass

class SpatialSeries(TimeSeries):

    _ancestry = "TimeSeries,SpatialSeries"
    
    _help = "Stores points in space over time. The data[] array structure is [num samples][num spatial dimensions]"

    def __init__(self, name, reference_frame=None):
        """Create a SpatialSeries TimeSeries dataset
            Arguments:
                *reference_frame* (string) Description defining what exactly 'straight-ahead' means.
        """
        super().__init__(name)
        self.reference_frame = reference_frame

    def set_data(self, data, conversion=None, resolution=None):
        super().set_data(data, "meter", conversion=conversion, resolution=resolution)

    def build_hdf5(self):
        builder = super().build_hdf5()
        builder.add_dataset("reference_frame", self.reference_frame)

    
