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

class TimeSeries(object):
    """ Standard TimeSeries constructor

        All time series are created by calls to  NWB.create_timeseries(). 
        They should not not be instantiated directly
    """
    def __init__(self, name, modality, spec, nwb):
        self.name = name
        # make a local copy of the specification, one that can be modified
        self.h5_builder = GroupBuilder()
        self.spec = copy.deepcopy(spec)
        # file handling
        self.nwb = nwb
        self.finalized = False
        # AJTRITT: Move modality into NWB class. 
        #          NWB class will decide where to store this TimeSeries object
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
        self.time_tgt_path = None
        self.data_tgt_path = None
        self.data_tgt_path_soft = None
        self.serial_num = -1

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

    # add a link to another NWB object
    def set_value_as_link(self, key, value):
        """ Create a link to another NWB object

            Arguments:
                *key* (text) Name of link as it will appear in *TimeSeries*

                *value* (text, TimeSeries or Interface) The object to
                be linked to, or the path to that object

            Returns:
                *nothing*
        """
        if self.finalized:
            self.fatal_error("Added value after finalization")
        # check type
        path = ""
        if isinstance(value, TimeSeries):
            path = value.full_path()
        elif isinstance(value, nwbmo.Interface):
            path = value.full_path()
        elif isinstance(value, str):
            path = value
        else:
            self.fatal_error("Unrecognized type for setting up link -- found %s" % type(value))
        # hack alert -- need to establish the definition for the field
        # this is already done in set_value, but that also sets the "_value"
        #   field. create the definition and then delete "_value" so the link
        #   can be established
        self.set_value(key, "dummy")
        del self.spec[key]["_value"]
        self.spec[key]["_value_hardlink"] = path
        self.set_value(key + "_path", path)

    # add a link to another NWB object
    def set_value_as_remote_link(self, key, target_file, dataset_path):
        """ Create a link to an NWB object in another file
        """
        assert False, "FINISH AND TEST FIRST"
        if self.finalized:
            self.fatal_error("Added value after finalization")
        # check type
        if not isinstance(target_file, str):
            self.fatal_error("File name must be string, received %s", type(target_file))
        if not isinstance(dataset_path, str):
            self.fatal_error("Dataset path must be string, received %s", type(dataset_path))
        # TODO set _value_softlink fields
        self.set_value(key, "????")
        extern_fields = self.spec["_attributes"]["extern_fields"]
        if "_value" not in extern_fields:
            extern_fields["_value"] = []
        extern_fields["_value"].append(key)
        self.set_value(key + "_link", target_file + "::" + dataset_path)

    # internal function used for setting data[] and timestamps[]
    # this method doesn't include necessary logic to manage attributes
    #   and prevent the user from adding custom attributes to
    #   standard fields, or to alter required 'custom' attribute
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
        self.h5_builder.set_attribute('description', value)

        if self.finalized:
            self.fatal_error("Added value after finalization")
        self.spec["_attributes"]["description"]["_value"] = str(value)

    def set_comments(self, value):
        """ Convenience function to set the comments field of the
            *TimeSeries*
        """
        self.h5_builder.set_attribute('comments', value)

        if self.finalized:
            self.fatal_error("Added value after finalization")
        self.spec["_attributes"]["comments"]["_value"] = str(value)

    # for backward compatibility to screwy scripts, and to be nice
    #   in event of typo
    def set_comment(self, value):
        self.set_comments(value)

    def set_source(self, value):
        """ Convenience function to set the source field of the
            *TimeSeries*
        """
        self.h5_builder.set_attribute('source', value)

        if self.finalized:
            self.fatal_error("Added value after finalization")
        self.spec["_attributes"]["source"]["_value"] = str(value)

    def set_time(self, timearray):
        ''' Store timestamps for the time series. 
   
           Arguments:
               *timearray* (double array) Timestamps for each element in *data*
   
           Returns:
               *nothing*
        '''
        self.h5_builder.add_dataset("timestamps", 
                                    timearray,
                                    attributes={"interval": 1, 
                                                "unit": "Seconds"})
        
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
        self.h5_builder.add_dataset("starting_time",
                                    time_zero, 
                                    attributes={"rate": rate})
        
        attrs = {}
        attrs["rate"] = rate
        self.set_value_with_attributes_internal("starting_time", time_zero, None, **attrs)

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
    def set_data(self, data, unit=None, conversion=None, resolution=None, dtype=None):
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
        attrs = {
            "unit": unit, 
            "conversion": conversion,
            "resolution": resolution
        }
        self.h5_builder.add_dataset("data", data, attributes=attrs)

        attrs = {}
        if unit is not None:
            attrs["unit"] = str(unit)
        if conversion is not None:
            attrs["conversion"] = float(conversion)
        if resolution is not None:
            attrs["resolution"] = float(resolution)
        self.set_value_with_attributes_internal("data", data, dtype, **attrs)

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
    # linking code

    # takes the path to the sibling time series to create a hard link
    #   to its timestamp array
    def set_time_as_link(self, sibling):
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
        self.h5_builder.add_soft_link('timestamps', sibling)

        if self.finalized:
            self.fatal_error("Added value after finalization")
        # it's possible that this TimeSeries path isn't set at the 
        #   time of the link (eg, if the TimeSeries is part of a
        #   module) so we can't register the path w/ the kernel yet.
        #   store link info for finalization, when path is known
        self.time_tgt_path = self.create_hardlink("timestamps", sibling)


    def set_data_as_link(self, sibling):
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
        self.h5_builder.add_soft_link('data', sibling)

        if self.finalized:
            self.fatal_error("Added value after finalization")
        # it's possible that this TimeSeries path isn't set at the 
        #   time of the link (eg, if the TimeSeries is part of a
        #   module) so we can't register the path w/ the kernel yet.
        #   store link info for finalization, when path is known
        self.data_tgt_path = self.create_hardlink("data", sibling)

    def set_data_as_remote_link(self, file_path, dataset_path):
        '''Links the *data* dataset in this TimeSeries to data stored
           in an external file, using and HDF5 soft-link.
           The dataset in the external file must contain attributes required 
           for the TimeSeries::data[] element.
   
           Arguments:
               *file_path* (text) File-system path to remote HDF5 file

               *dataset_path* (text) Full path within remote HDF5 file to dataset
   
           Returns:
               *nothing*
        '''
        self.h5_builder.add_external_link('data', file_path, dataset_path)

        if self.finalized:
            self.fatal_error("Added value after finalization")
        self.create_softlink("data", file_path, dataset_path)
        # it's possible that this TimeSeries path isn't set at the 
        #   time of the link (eg, if the TimeSeries is part of a
        #   module) so we can't register the path w/ the kernel yet.
        #   store link info for finalization, when path is known
        self.data_tgt_path_soft = file_path + "://" + dataset_path
        #self.nwb.record_timeseries_data_soft_link(self.full_path(), file_path+"://"+dataset_path)
        extern_fields = self.spec["_attributes"]["extern_fields"]
        if "_value" not in extern_fields:
            extern_fields["_value"] = []
        extern_fields["_value"].append("data")


    # internal function
    # creates link to similarly named field between two groups
    def create_hardlink(self, field, target):
        # type safety -- make sure sibling is class if not string
        if self.finalized:
            self.fatal_error("Added value after finalization")
        if isinstance(target, str):
            sib_path = target
        elif isinstance(target, TimeSeries):
            sib_path = target.full_path()
        elif isinstance(target, nwbmo.Module):
            sib_path = target.full_path()
        else:
            self.fatal_error("Unrecognized link-to object. Expected str or TimeSeries, found %s" % type(target))
        # define link. throw error if value was already set
        if "_value" in self.spec[field]:
            self.fatal_error("cannot specify a link after setting value")
        elif "_value_softlink" in self.spec[field]:
            self.fatal_error("cannot specify both hard and soft links")
        self.spec[field]["_value_hardlink"] = sib_path + "/" + field
        # return path string
        return sib_path


    # internal function
    # creates link to similarly named field between two groups
    def create_softlink(self, field, file_path, dataset_path):
        if self.finalized:
            self.fatal_error("Added value after finalization")
        if "_value" in self.spec[field]:
            self.fatal_error("cannot specify a data link after set_data()")
        elif "_value_hardlink" in self.spec[field]:
            self.fatal_error("cannot specify both hard and soft links")
        self.spec[field]["_value_softlink"] = dataset_path
        self.spec[field]["_value_softlink_file"] = file_path


    ####################################################################
    ####################################################################
    # file writing and path management

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

    def full_path(self):
        """ Returns the HDF5 path to this *TimeSeries*

            Arguments: 
                *none*

            Returns:
                *nothing*
        """
        return self.path + self.name

    def finalize(self):
        """ Finish the *TimeSeries* and write pending changes to disk

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
    def __init__(self, name, modality, spec, nwb):
        super(AnnotationSeries, self).__init__(name, modality, spec, nwb)
        self.annot_str = []
        self.annot_time = []

    def add_annotation(self, what, when):
        '''Convennece function to add annotations individually

        Arguments:
            *what* (text) Annotation

            *when* (double) Timestamp for annotation

        Returns:
            *nothing*
        '''
        self.annot_str.append(str(what))
        self.annot_time.append(float(when))

    def finalize(self):
        '''Extends superclass call by pushing annotations onto 
        the data[] and timestamps[] fields

        Arguments:
            *none*

        Returns:
            *nothing*
        '''
        if self.finalized:
            return
        if len(self.annot_str) > 0:
            if "_value" in self.spec["data"]:
                print("AnnotationSeries error -- can only call set_data() or add_annotation(), not both")
                print("AnnotationSeries name: " + self.name)
                sys.exit(1)
            if "_value" in self.spec["timestamps"]:
                print("AnnotationSeries error -- can only call set_time() or add_annotation(), not both")
                print("AnnotationSeries name: " + self.name)
                sys.exit(1)
            self.spec["data"]["_value"] = self.annot_str
            self.spec["timestamps"]["_value"] = self.annot_time
        super(AnnotationSeries, self).finalize()

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

    def set_features(self, names, units):
        """ Convenience function for setting feature values. Has logic to
            ensure arrays have equal length (ie, sanity check)

            Arguments:
                *names* (text array) Description of abstract features

                *units* (text array) Units for each of the abstract features

            Returns:
                *nothing*
        """
        # sanlty checks
        # make sure both are arrays, not strings
        if isinstance(names, str):
            names = [ str(names) ]
        if isinstance(units, str):
            units = [ str(units) ]
        # make sure arrays are of same length
        if len(names) != len(units):
            self.fatal_error("name and unit vectors must have equal length")
        self.set_value("features", names)
        self.set_value("feature_units", units)

