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
import os.path
import shutil
import time
import json
import traceback
import h5py
import copy
import numpy as np
import h5tools
from . import nwbts
from . import nwbep
from . import nwbmo

from . import container

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

# merge dict y into dict x
def recursive_dictionary_merge(x, y):
    for key in y:
        if key in x:
            if isinstance(x[key], dict) and isinstance(y[key], dict):
                recursive_dictionary_merge(x[key], y[key])
            elif x[key] != y[key]:
                x[key] = y[key]
        else:
            x[key] = y[key]
    return x

def load_json(fname):
    # correct the path, in case calling from remote directory
    fname = os.path.join( os.path.dirname(__file__), fname)
    try:
        with open(fname, 'r') as f:
            jin = json.load(f)
            f.close()
    except IOError:
        print("Unable to load json file '%s'" % fname)
        sys.exit(1)
    return jin

def load_yaml(fname):
    import yaml
    # correct the path, in case calling from remote directory
    fname = os.path.join( os.path.dirname(__file__), fname)
    try:
        with open(fname, 'r') as f:
            jin = yaml.load(f)
            f.close()
    except IOError:
        print("Unable to load json file '%s'" % fname)
        sys.exit(1)
    return jin

def load_spec_file(fname):
    if fname.endswith(".yml"):
        return load_yaml(fname)
    elif fname.endswith(".yaml"):
        return load_yaml(fname)
    else: # try json as default
        return load_json(fname)

def load_spec(custom_spec):
    spec = load_spec_file("spec_file.json")
    ts = load_spec_file("spec_ts.json")
    recursive_dictionary_merge(spec, ts)
    mod = load_spec_file("spec_mod.json")
    recursive_dictionary_merge(spec, mod)
    iface = load_spec_file("spec_iface.json")
    recursive_dictionary_merge(spec, iface)
    gen = load_spec_file("spec_general.json")
    recursive_dictionary_merge(spec, gen)
    ep = load_spec_file("spec_epoch.json")
    recursive_dictionary_merge(spec, ep)
    if len(custom_spec) > 0:
        custom = load_spec_file(custom_spec)
        recursive_dictionary_merge(spec, custom)
    #write_json("fullspec.json", spec)
    return spec

def write_json(fname, js):
    with open(fname, "w") as f:
        json.dump(js, f, indent=2)
        f.close()

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

def register_finalization(name, num):
    global object_register
    if str(num) not in object_register:
        print("Serial number error (SN=%d)" % num)
        print("Object '" + name + "' declared final but was never registered")
        print("Stack trace follows")
        print("-------------------")
        traceback.print_stack()
        sys.exit(1)
    if object_register[str(num)] is None:
        print("Object '" + name + "' finalized multiple times")
        print("Stack trace follows")
        print("-------------------")
        traceback.print_stack()
        sys.exit(1)
    object_register[str(num)] = None

def check_finalization():
    global object_register, serial_number
    err = False
    for k, v in object_register.items():
        if v is not None:
            if not err:
                print("----------------------------------")
                print("Finalization error")
            err = True
            print("    object '"+v+"' was not finalized")
    if err:
        sys.exit(1)


TS_MOD_ACQUISITION = 'acquisition'
TS_MOD_STIMULUS = 'stimulus'
TS_MOD_TEMPLATE = 'template'
TS_MOD_OTHER = 'other'
    

# TODO some functionality will be broken on append operations. in particular
#   when an attribute stores a list of links, that list will not be
#   properly updated if new links are created during append  FIXME

class NWB(container.Container):
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
                "u1": 'uint8'
                "byte": 'uint8'
    }


    def __init__(self, **vargs):
        super().__init__()
        self.__read_arguments__(**vargs)

        self.__timeseries = {
            TS_MOD_ACQUISITION: dict(),
            TS_MOD_STIMULUS: dict(),
            TS_MOD_TEMPLATE: dict(),
            TS_MOD_OTHER: dict(),
        }

        self.__modalities = dict()

        self.modules = dict()

    @property
    def acquisition_timeseries(self):
        return self.__timeseries[TS_MOD_ACQUISITION]

    @property
    def stimulus_timeseries(self):
        return self.__timeseries[TS_MOD_STIMULUS]

    @property
    def template_timeseries(self):
        return self.__timeseries[TS_MOD_TEMPLATE]

    @property
    def other_timeseries(self):
        return self.__timeseries[TS_MOD_OTHER]

    @property
    def timeseries(self):
        return self.__timeseries

    def get_timeseries_modality(self, ts):
        return self.__modalities[ts]

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

    ####################################################################
    ####################################################################
    # File operations

    # create file content

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
        spec = self.spec["Epoch"]
        epo = nwbep.Epoch(name, self, start, stop, spec)
        self.epoch_list.append(epo)
        epo.serial_num = register_creation("Epoch -- " + name)
        return epo

    def create_timeseries(self, name, ts_type="TimeSeries", modality=TS_MOD_OTHER):
        """ Creates a new TimeSeries object. Timeseries are used to
            store and associate data or events with the time the
            data/events occur.

            Arguments:
                *ts_type* (text) The type of timeseries to be created.
                Default options are:

                    TimeSeries -- simple time series

                    AbstractFeatureSeries -- features of a presented
                    stimulus. This is particularly useful when storing
                    the raw stimulus is impractical and only certain
                    features of the stimulus are salient. An example is
                    the visual stimulus of orientation gratings, where
                    the phase, spatial/temporal frequency and contrast
                    are relevant, but the individual video frames are
                    impractical to store, and not as useful

                    AnnotationSeries -- stores strings that annotate
                    events or actions, plus the time the annotation was made

                    ElectricalSeries -- Voltage acquired during extracellular
                    recordings

                    ImageSeries -- storage object for 2D image data. An
                    ImageSeries can represent image data within the file
                    or can point to an image stack in an external file
                    (eg, png or tiff)

                    IndexSeries -- series that is composed of samples
                    in an existing time series, for example images that
                    are pulled from an image stack in random order

                    ImageMaskSeries -- a mask that is applied to a visual
                    stimulus

                    IntervalSeries -- a list of starting and stop times
                    of events

                    OpticalSeries -- a series of image frames, such as for
                    video stimulus or optical recording
                    
                    OptogeneticSeries -- optical stimulus applied during
                    an optogentic experiment

                    RoiResponseSeries -- responses of a region-of-interest
                    during optical recordings, such as florescence or dF/F

                    SpatialSeries -- storage of points in space over time

                    SpikeEventSeries -- snapshots of spikes events in
                    an extracellular recording

                    TwoPhotonSeries -- Image stack recorded from a 
                    2-photon microscope

                    VoltageClampSeries, CurrentClampSeries -- current or
                    voltage recurded during a patch clamp experiment

                    VoltageClampStimulusSeries, CurrentClampStimulusSeries
                    -- voltage or current used as stimulus during a
                    patch clamp experiment

                    WidefieldSeries -- Image stack recorded from wide-field
                    imaging

                *name* (text) the name of the TimeSeries, as it will
                appear in the file

                *modality* (text) this indicates where in the file the
                TimeSeries will be stored. Values are:

                    'acquisition' -- acquired data stored under 
                    /acquisition/timeseries

                    'stimulus' -- stimulus data stored under
                    /stimulus/presentations

                    'template' -- a template for a stimulus, useful if
                    a stimulus will be repeated as it only has to be
                    stored once

                    'other' (DEFAULT) -- TimeSeries is to be used in a 
                    module, in which case the module will manage its
                    placement, or it's up to the user where to place it

            Returns:
                TimeSeries object
        """
        # BEGIN: AJTRITT code
        ts_class = getattr(nwbts, ts_type, None)
        if not ts_class:
            raise ValueError("%s is an invalid TimeSeries type" % ts_type)
        if modality not in TS_LOCATION:
            raise ValueError("%s is not a valid TimeSeries modality" % modality)
        ts = ts_class(name, parent=self)
        self.__timeseries[modality][name] = ts
        self.__modalities[ts] = modality

        return self.__timeseries[modality][name]
        #self.builder[TS_LOCATION[modality]][name] = ts_class(name)
        #return self.builder[TS_LOCATION[modality]][name]
        # END: AJTRITT code
        # find time series by name
        # recursively examine spec and create dict of required fields

    def create_module(self, name):
        """ Creates a Module object of the specified name. Interfaces can
            be created by the module and will be stored inside it

            Arguments:
                *name* (text) Name of the module as it will appear in the
                file (under /processing/)

            Returns:
                Module object
        """
        self.modules[name] = Module(name)
        return self.modules[name]

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
        
