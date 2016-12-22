# Copyright (c) 2015 Allen Institute, California Institute of Technology, 
# New York University School of Medicine, the Howard Hughes Medical 
# Institute, University of California, Berkeley, GE, the Kavli Foundation 
# and the International Neuroinformatics Coordinating Facility. 
# All rights reserved.
#     
# Redistribution and use in source and binary forms, with or without 
# modification, are permitted provided that the following 
# conditions are met:
#     
# 1.  Redistributions of source code must retain the above copyright 
#     notice, this list of conditions and the following disclaimer.
#     
# 2.  Redistributions in binary form must reproduce the above copyright 
#     notice, this list of conditions and the following disclaimer in 
#     the documentation and/or other materials provided with the distribution.
#     
# 3.  Neither the name of the copyright holder nor the names of its 
#     contributors may be used to endorse or promote products derived 
#     from this software without specific prior written permission.
#     
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS 
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT 
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS 
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE 
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, 
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN 
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
import sys
import os.path
import shutil
import time
import json
import traceback
import h5py
import copy
import numpy as np
import types


from . import timeseries as _timeseries
from .module import Module
from .epoch import Epoch
from .ephys import ElectrodeGroup

from ..core import docval
from .container import nwbproperties, NwbContainer

VERS_MAJOR = 1
VERS_MINOR = 0
VERS_PATCH = 5

__version__ = "%d.%d.%d" % (VERS_MAJOR, VERS_MINOR, VERS_PATCH)
FILE_VERSION_STR = "NWB-%s" % __version__

def get_major_vers():
    return VERS_MAJOR

def get_minor_vers():
    return VERS_MINOR

def get_patch_vers():
    return VERS_PATCH

def get_file_vers_string():
    return FILE_VERSION_STR

def create_identifier(base_string):
    """ Creates an identifying string for the file, hopefully unique 
        in and between labs, based on the supplied base string, the NWB file
        version, and the time the file was created. The base string
        should contain the name of the lab, experimenter and project, or
        some other string that is unique to a given lab
    """
    return base_string + "; " + FILE_VERSION_STR + "; " + time.ctime()


# it is too easy to create an object and forget to finalize it
# keep track of when each object is created and finalized, and
#   provide a way to detect when finalization doesnt occur
serial_number = 0
object_register = {}
def register_creation(name):
    global serial_number, object_register
    num = serial_number
    object_register[str(num)] = name
    serial_number += 1
    return num


# TODO some functionality will be broken on append operations. in particular
#   when an attribute stores a list of links, that list will not be
#   properly updated if new links are created during append  FIXME

class NWBFile(NwbContainer):
    """ Represents an NWB file. Calling the NWB constructor creates the file.
        The following arguments are recognized:

            **filename** (text -- mandatory) The name of the to-be-created 
            file

            **identifier** (text -- mandatory) A unique identifier for
            the file, to differentiate it from all other files (even in
            other labs). A suggested way to create the identifier is to
            use a lab-specific string and send it to
            nwb.create_identifier(string). This function returns the
            supplied string appended by the present date

            **description** (text -- mandatory) A one or two sentence
            description of the experiment and what the data in the file
            represents

            *start_time* (text -- optional) This is the starting time of the 
            experiment.  If this isn't provided, the start time of the 
            experiment will default to the time that the file is created

            *modify* (boolean -- optional) Opens the file in append mode
            if the file exists. If the file exists and this flag (or
            'overwrite') is not set, an error occurs (to prevent
            accidentally overwriting or modifying an existing file)

            *overwrite* (boolean -- optional) If the specified file exists,
            it will be overwritten

            *keep_original* (boolean -- optional) -- If true, a back-up copy 
            of the original file will be kept, named '<filename>.prev'

            *auto_compress* (boolean -- optional) Data is compressed
            automatically through the API. Setting 'auto_compress=False'
            disables this behavior

            *custom_spec* (text -- optional) A json, yaml or toml file
            used to customize the format specification (pyyaml or toml
            must be installed to use those formats)
    """
    dtype_glossary = {
                "float32": 'f4',
                "float4": 'f4',
                "float64": 'f8',
                "float8": 'f8',
                "text": 'str',
                "i8": 'int64',
                "i4": 'int32',
                "i2": 'int16',
                "i1": 'int8',
                "u8": 'uint64',
                "u4": 'uint32',
                "u2": 'uint16',
                "u1": 'uint8',
                "byte": 'uint8'
    }


    @docval({'name': 'file_name', 'type': str, 'doc': 'path to NWB file'})
    def __init__(self, **vargs):
        super().__init__()
        self._filename = getargs('file_name', **vargs)
        self.__read_arguments__(**vargs)

        self.__rawdata = dict()
        self.__stimulus = dict()
        self.__stimulus_template = dict()

        self.modules = dict()
        self.epochs = dict()
        self.electrodes = dict()

    @property
    def rawdata(self):
        return tuple(self.__rawdata.values())

    @property
    def stimulus(self):
        return tuple(self.__stimulus.values())

    @property
    def stimulus_template(self):
        return tuple(self.__stimulus_template.values())

    def is_rawdata(self, ts):
        return self.__exists(ts, self.__rawdata)

    def is_stimulus(self, ts):
        return self.__exists(ts, self.__stimulus)

    def is_stimulus_template(self, ts):
        return self.__exists(ts, self.__stimulus_template)

    def __exists(self, ts, d):
        return ts.name in d

    # internal API function to process constructor arguments
    def __read_arguments__(self, **vargs):
        err_str = ""
        # file name
        if "filename" in vargs:
            self.file_name = vargs["filename"]
        elif "file_name" in vargs:
            self.file_name = vargs["file_name"]
        else:
            err_str += "    argument '%s' was not specified\n" % "filename"
        # see if file exists -- some arguments aren't required if so
        if os.path.isfile(self.file_name):
            self.file_exists = True
        else:
            self.file_exists = False
        # read start time
        if "start_time" in vargs:
            self.start_time = vargs["start_time"]
            del vargs["start_time"]
        elif "starting_time" in vargs:
            self.start_time = vargs["starting_time"]
            del vargs["starting_time"]
        else:
            self.start_time = time.ctime()
        if "auto_compress" in vargs:
            self.auto_compress = vargs["auto_compress"]
        else:
            self.auto_compress = True
        # allow user to specify custom json specification file
        # when the request to specify multiple files comes in, allow
        #   multiple files to be submitted as a dictionary or list
        if "custom_spec" in vargs:
            self.custom_spec = vargs["custom_spec"]
        else:
            self.custom_spec = []
        # read identifier
        if "identifier" in vargs:
            self.file_identifier = vargs["identifier"]
        elif not self.file_exists:
            err_str += "    argument '%s' was not specified\n" % "identifier"
        # read session description
        if "description" in vargs:
            self.session_description = vargs["description"]
        elif not self.file_exists:
            err_str += "    argument 'description' was not specified\n"
        # handle errors
        if len(err_str) > 0:
            print("Error creating Borg object - missing constructor value(s)")
            print(err_str)
            sys.exit(1)

    def create_epoch(self, name, start, stop):
        """ Creates a new Epoch object. Epochs are used to track intervals
            in an experiment, such as exposure to a certain type of stimuli
            (an interval where orientation gratings are shown, or of 
            sparse noise) or a different paradigm (a rat exploring an 
            enclosure versus sleeping between explorations)

            Arguments:
                *name* (text) The name of the epoch, as it will appear in
                the file

                *start* (float) The starting time of the epoch

                *stop* (float) The ending time of the epoch

            Returns:
                Epoch object
        """
        epoch = Epoch(name, start, stop)
        self.epochs[name] = epoch
        return epoch

    def get_epoch(self, name):
        return self.__get_epoch(name)

    @docval({'name': 'epoch', 'type': (str, Epoch), 'doc': 'the name of an epoch or an Epoch object or a list of names of epochs or Epoch objects'},
            {'name': 'timeseries', 'type': (str, _timeseries.TimeSeries), 'doc': 'the name of a timeseries or a TimeSeries object or a list of names of timeseries or TimeSeries objects'})
    def set_epoch_timeseries(self, **kwargs):
        """Add one or more TimSeries datasets to one or more Epochs
        """
        epoch, timeseries = getargs('epoch', 'timeseries', **kwargs)
        if isinstance(epochs, list):
            ep_objs = [self.__get_epoch(ep) for ep in epochs]
        else:
            ep_objs = [self.__get_epoch(epochs)]

        if isinstance(timeseries, list):
            ts_objs = [self.__get_timeseries(ts) for ts in timeseries]
        else:
            ts_objs = [self.__get_timeseries(timeseries)]

        for ep in ep_objs:
            for ts in ts_objs:
                ep.add_timeseries(ts)

    def __get_epoch(self, epoch):
        if isinstance(epoch, Epoch):
            ep = epoch
        elif isinstance(epoch, str): 
            ep = self.epochs.get(epoch)
            if not ep:
                raise KeyError(epoch)
        else:
            raise TypeError(type(epoch))
        return ep

    def __get_timeseries(self, timeseries):
        if isinstance(timeseries, _timeseries.TimeSeries):
            ts = timeseries 
        elif isinstance(timeseries, str): 
            mod = self.modality.get(timeseries)
            if not mod:
                raise KeyError(timeseries)
            ts = self.__timeseries[mod][timeseries]
        else:
            raise TypeError(type(timeseries))
        return ts

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the timeseries dataset'},
            {'name': 'ts_type', 'type': type, 'doc': 'the type of timeseries to be created. See :py:meth:`~pynwb.timeseries.TimeSeries` subclasses for options' },
            {'name': 'epoch', 'type': (str, Epoch), 'doc': 'the name of an epoch or an Epoch object or a list of names of epochs or Epoch objects'},
            returns="the TimeSeries object")
    def create_timeseries(self, **kwargs):
        """ Creates a new TimeSeries object. Timeseries are used to
            store and associate data or events with the time the
            data/events occur.
        """
        name, ts_type, modality, epoch = getargs('name', 'ts_type', 'modality', 'epoch', **kwargs)
        ts_class = getattr(_timeseries, ts_type, None)
        if not ts_class:
            raise ValueError("%s is an invalid TimeSeries type" % ts_type)
        if modality not in TS_LOCATION:
            raise ValueError("%s is not a valid TimeSeries modality" % modality)
        ts = ts_class(name, parent=self)
        self.__timeseries[modality][name] = ts
        self.add_timeseries(ts, modality=modality, epoch=epoch)
        return self.__timeseries[modality][name]

    def link_timeseries(self, ts):
        pass

    @docval({'name': 'ts', 'type': _timeseries.TimeSeries, 'doc': 'the  TimeSeries object to add'},
            {'name': 'epoch', 'type': (str, Epoch), 'doc': 'the name of an epoch or an Epoch object or a list of names of epochs or Epoch objects', 'default': None},
            returns="the TimeSeries object")
    def add_raw_data(self, **kwargs):
        ts, epoch = getargs('ts', 'epoch', **kwargs)
        self.__set_timeseries(self.__rawdata, ts, epoch)

    @docval({'name': 'ts', 'type': _timeseries.TimeSeries, 'doc': 'the  TimeSeries object to add'},
            {'name': 'epoch', 'type': (str, Epoch), 'doc': 'the name of an epoch or an Epoch object or a list of names of epochs or Epoch objects', 'default': None},
            returns="the TimeSeries object")
    def add_stimulus(self, **kwargs):
        ts, epoch = getargs('ts', 'epoch', **kwargs)
        self.__set_timeseries(self.__stimulus, ts, epoch)

    @docval({'name': 'ts', 'type': _timeseries.TimeSeries, 'doc': 'the  TimeSeries object to add'},
            {'name': 'epoch', 'type': (str, Epoch), 'doc': 'the name of an epoch or an Epoch object or a list of names of epochs or Epoch objects', 'default': None},
            returns="the TimeSeries object")
    def add_stimulus_template(self, **kwargs):
        ts, epoch = getargs('ts', 'epoch', **kwargs)
        self.__set_timeseries(self.__stimulus_template, ts, epoch)

    def __set_timeseries(self, ts_dict, ts, epoch=None):
        ts_dict[ts.name] = ts
        ts.set_parent(self)
        if epoch:
            self.set_epoch_timeseries(epoch, ts)
    
    def set_metadata(self, key, value, **attrs):
        """ Creates a field under /general/ and stores the specified
            information there. 
            NOTE: using the constants defined in nwbco.py is strongly
            encouraged, as this will help prevent accidental typos
            and will not require the user to remember where a particular
            piece of data is to be stored

            Arguments:
                *key* (text) Name of the metadata field. Please use the
                constants and functions defined in nwbco.py

                *value* Value of the data to be stored. This will be text
                in most cases

                *attrs* (dictionary, or key/value pairs) Attributes that
                will be created on the metadata field

            Returns:
                nothing
        """
        if type(key).__name__ == "function":
            self.fatal_error("Function passed instead of string or constant -- please see documentation for usage of '%s'" % key.__name__)
        # metadata fields are specified using hdf5 path
        # all paths relative to general/
        toks = key.split('/')
        # get specification and store data in appropriate slot
        spec = self.spec["General"]
        n = len(toks)
        for i in range(n):
            if toks[i] not in spec:
                # support optional fields/directories
                # recurse tree to find appropriate element
                if i == n-1 and "[]" in spec:
                    spec[toks[i]] = copy.deepcopy(spec["[]"])   # custom field
                    spec = spec[toks[i]]
                elif i < n-1 and "<>" in spec:
                    # variably named group
                    spec[toks[i]] = copy.deepcopy(spec["<>"])
                    spec = spec[toks[i]]
                else:
                    self.fatal_error("Unable to locate '%s' of %s in specification" % (toks[i], key))
            else:
                spec = spec[toks[i]]
        self.check_type(key, value, spec["_datatype"])
        spec["_value"] = value
        # handle attributes
        if "_attributes" not in spec:
            spec["_attributes"] = {}
        for k, v in attrs.items():
            if k not in spec["_attributes"]:
                spec["_attributes"][k] = {}
            fld = spec["_attributes"][k]
            fld["_datatype"] = 'str'
            fld["_value"] = str(v)

    def set_metadata_from_file(self, key, filename, **attrs):
        """ Creates a field under /general/ and stores the contents of
            the specified file in that field
            NOTE: using the constants defined in nwbco.py is strongly
            encouraged, as this will help prevent accidental typos
            and will not require the user to remember where a particular
            piece of data is to be stored

            Arguments:
                *key* (text) Name of the metadata field. Please use the
                constants and functions defined in nwbco.py

                *filename* (text) Name of file containing the data to 
                be stored

                *attrs* (dictionary, or key/value pairs) Attributes that
                will be created on the metadata field

            Returns:
                nothing
        """
        try:
            f = open(filename, 'r')
            contents = f.read()
            f.close()
        except IOError:
            self.fatal_error("Error opening metadata file " + filename)
        self.set_metadata(key, contents, **attrs)

    def create_reference_image(self, stream, name, fmt, desc, dtype=None):
        """ Adds documentation image (or movie) to file. This is stored
            in /acquisition/images/.

            Args:
                *stream* (binary) Data stream of image (eg, binary contents of .png image)

                *name* (text) Name that image will be stored as

                *fmt* (text) Format of the image (eg, "png", "avi")

                *desc* (text) Descriptive text describing the image

                *dtype* (text) Optional field specifying the h5py datatype to use to store *stream*

            Returns:
                *nothing*
        """
        fp = self.file_pointer
        img_grp = fp["acquisition"]["images"]
        if name in img_grp:
            self.fatal_error("Reference image %s alreayd exists" % name)
        if dtype is None:
            img = img_grp.add_dataset(name, stream)
        else:
            img = img_grp.add_dataset(name, stream, dtype=dtype)
        img.set_attribute("format", np.string_(fmt))
        img.set_attribute("description", np.string_(desc))
        

    @docval({'name': 'name',  'type': str,   'doc': 'the name of the electrode group'},
            {'name': 'coord', 'type': tuple, 'doc': 'the xyz-coordinates of this electrode group'},
            {'name': 'desc',  'type': str,   'doc': 'a description of the probe/shank/tetrode'},
            {'name': 'dev',   'type': str,   'doc': 'name of the device this probe/shank/tetrode is from'},
            {'name': 'loc',   'type': str,   'doc': 'description of electrode location'},
            returns='the electrode group', rtype=ElectrodeGroup)
    def create_electrode_group(self, **kwargs):
        """Add an electrode group (e.g. a probe, shank, tetrode). 
        """
        name, coord, desc, dev, loc = getargs('name', 'coord', 'desc', 'dev', 'loc', **kwargs)
        elec_grp = ephys.ElectrodeGroup(name, coord, desc, dev, loc)
        elec_grp.parent = self
        self.electrodes[name] = elec_grp
        return elec_grp

    def set_electrode_group(self, name, elec_grp):
        self.electrodes[name] = elec_grp

    def get_electrode_group(self, name):
        return self.electrodes.get(name)

    @docval({'name': 'processing_name',  'type': str,   'doc': 'the processing analysis name'},
            returns="a processing module", rtype=Module)
    def create_processing_module(self, **kwargs):
        """ Creates a Module object of the specified name. Interfaces can
            be created by the module and will be stored inside it
        """
        processing_name = get_args('processing_name', **kwargs)
        self.modules[processing_name] = Module(processing_name)
        return self.modules[processing_name]

    @docval({'name': 'name',  'type': str, 'doc': 'the name of the electrophysiology dataset'},
            {'name': 'data',  'type': (np.ndarray, list, types.GeneratorType), 'doc': 'the name of the electrophysiology dataset'},
            {'name': 'elec_ids',  'type': str, 'doc': 'the ID of the electrode each channel belongs to'},
            {'name': 'timestamps', 'type': (np.ndarray, list, types.GeneratorType), 'doc': 'the timestamps for this dataset', 'default': None},
            {'name': 'start_rate', 'type': (tuple, list), 'doc': 'tuple containing start time and sample rate', 'default': None},
            returns="a processing module", rtype=_timeseries.ElectricalSeries)
    def add_ephys_data(self, **kwargs):
        name, data, elec_id, timestamps, start_rate = getargs("name", "data", "elec_id", "timestamps", "start_rate", **kwargs)
        ts = _timeseries.ElectricalSeries(name, electrodes=elec_id)
        ts.set_data(data)
        if timestamps:
            ts.set_timestamps(timestamps)
        elif start_rate:
            ts.set_time_by_rate(start_rate[0], start_rate[1])
        return ts

