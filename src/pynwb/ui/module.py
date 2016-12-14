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
import math
import numpy as np

from .import ephys as _ephys

from .container import properties, Container

class Module(Container):
    """ Processing module. This is a container for one or more interfaces
        that provide data at intermediate levels of analysis

        Modules should be created through calls to NWB.create_module().
        They should not be instantiated directly
    """
    def __init__(self, name, nwb, spec):
        self.name = name
        self.nwb = nwb
        self.spec = copy.deepcopy(spec)
        # a place to store interfaces belonging to this module
        self.ifaces = {}
        # create module folder immediately, so it's available 
        folder = self.nwb.file_pointer["processing"]
        if name in folder:
            nwb.fatal_error("Module '%s' already exists" % name)
        self.mod_folder = folder.create_group(self.name)
        self.serial_num = -1
        # 
        self.finalized = False

    def full_path(self):
        """ Returns HDF5 path of module

            Arguments:
                *none*

            Returns:
                (text) the HDF5 path to the module
        """
        return "processing/" + self.name

    def __build_electrical_ts(self, data, electrode_indices, timestamps=None, start_rate=None, name='data'):
        ts = nwbts.ElectricalSeries(name, electrodes=electrode_indices)
        ts.set_data(data)
        if timestamps:
            ts.set_timestamps(timestamps)
        elif start_rate:
            ts.set_time_by_rate(start_rate[0], start_rate[1])
        return ts

    def add_lfp(self, data, electrode_indices, timestamps=None, start_rate=None, name='data'):
        ts = self.__build_electrical_ts(data, 
                                        electrode_indices,
                                        timestamps=timestamps,
                                        start_rate=start_rate)
        iface = _ephys.LFP(lfp_ts=ts)
        return iface

    def add_filtered_ephys(self, data, electrode_indices, timestamps=None, start_rate=None, name='data'):
        ts = self.__build_electrical_ts(data, 
                                        electrode_indices,
                                        timestamps=timestamps,
                                        start_rate=start_rate,
                                        name=name)
        iface = _ephys.FilteredEphys(ephys_ts=ts)
        return iface

        
#    def create_interface(self, iface_type):
#        """ Creates an interface within the module. 
#            Each module can have multiple interfaces.
#            Standard interface options are:
#
#                BehavioralEpochs -- general container for storing and
#                publishing intervals (IntervalSeries)
#
#                BehavioralEvents -- general container for storing and
#                publishing event series (TimeSeries)
#
#                BehavioralTimeSeries -- general container for storing and
#                publishing time series (TimeSeries)
#
#                Clustering -- clustered spike data, whether from
#                automatic clustering tools or as a result of manual
#                sorting
#
#                ClusterWaveform -- mean event waveform of clustered data
#
#                CompassDirection -- publishes 1+ SpatialSeries storing
#                direction in degrees (or radians) 
#
#                DfOverF -- publishes 1+ RoiResponseSeries showing
#                dF/F in observed ROIs
#
#                EventDetection -- information about detected events
#
#                EventWaveform -- publishes 1+ SpikeEventSeries
#                of extracellularly recorded spike events
#
#                EyeTracking -- publishes 1+ SpatialSeries storing 
#                direction of gaze
#
#                FeatureExtraction -- salient features of events
#
#                FilteredEphys -- publishes 1+ ElectricalSeries storing
#                data from digital filtering
#
#                Fluorescence -- publishes 1+ RoiResponseSeries showing
#                fluorescence of observed ROIs
#
#                ImageSegmentation -- publishes groups of pixels that
#                represent regions of interest in an image
#
#                LFP -- a special case of FilteredEphys, filtered and
#                downsampled for LFP signal
#
#                MotionCorrection -- publishes image stacks whos frames
#                have been corrected to account for motion
#
#                Position -- publishes 1+ SpatialSeries storing physical
#                position. This can be along x, xy or xyz axes
#
#                PupilTracking -- publishes 1+ standard *TimeSeries* 
#                that stores pupil size
#
#                UnitTimes -- published data about the time(s) spikes
#                were detected in an observed unit
#        """
#        iface_class = getattr(sys.modules[__name__], iface_type, None)
#        
#        self.interfaces[name] = iface_class(if_spec)
#
#        if iface_type not in self.nwb.spec["Interface"]:
#            self.nwb.fatal_error("unrecognized interface: " + iface_type)
#        if_spec = self.create_interface_definition(iface_type)
#        if iface_type == "ImageSegmentation":
#            iface = ImageSegmentation(iface_type, self, if_spec)
#        elif iface_type == "Clustering":
#            iface = Clustering(iface_type, self, if_spec)
#        elif iface_type == "ImagingRetinotopy":
#            iface = ImagingRetinotopy(iface_type, self, if_spec)
#        elif iface_type == "UnitTimes":
#            iface = UnitTimes(iface_type, self, if_spec)
#        elif iface_type == "MotionCorrection":
#            iface = MotionCorrection(iface_type, self, if_spec)
#        else:
#            iface = Interface(iface_type, self, if_spec)
#        self.ifaces[iface_type] = iface
#        from . import nwb as nwblib
#        iface.serial_num = nwblib.register_creation("Interface -- " + iface_type)
#        return iface
#
#    # internal function
#    # read spec to create time series definition. do it recursively 
#    #   if time series are subclassed
#    def create_interface_definition(self, if_type):
#        super_spec = copy.deepcopy(self.nwb.spec["Interface"]["SuperInterface"])
#        if_spec = self.nwb.spec["Interface"][if_type]
#        from . import nwb as nwblib
#        return nwblib.recursive_dictionary_merge(super_spec, if_spec)
#
#    def set_description(self, desc):
#        """ Set description field in module
#
#            Arguments:
#                *desc* (text) Description of module
#
#            Returns:
#                *nothing*
#        """
#        self.set_value("description", desc)
#
#    def set_value(self, key, value, **attrs):
#        """Adds a custom key-value pair (ie, dataset) to the root of 
#           the module.
#   
#           Arguments:
#               *key* (string) A unique identifier within the TimeSeries
#
#               *value* (any) The value associated with this key
#
#               *attrs* (dict) Dictionary of key-value pairs to be
#               stored as attributes
#   
#           Returns:
#               *nothing*
#        """
#        if self.finalized:
#            self.nwb.fatal_error("Added value to module after finalization")
#        self.spec[key] = copy.deepcopy(self.spec["[]"])
#        dtype = self.spec[key]["_datatype"]
#        name = "module " + self.name
#        self.nwb.set_value_internal(key, value, self.spec, name, dtype, **attrs)
#
#    def finalize(self):
#        """ Completes the module and writes changes to disk.
#
#            Arguments: 
#                *none*
#
#            Returns:
#                *nothing*
#        """
#        if self.finalized:
#            return
#        self.finalized = True
#        # finalize interfaces
#        iface_names = []
#        for k, v in self.ifaces.items():
#            v.finalize()
#            iface_names.append(v.name)
#        iface_names.sort()
#        self.spec["_attributes"]["interfaces"]["_value"] = iface_names
#        # write own data
#        grp = self.nwb.file_pointer["processing/" + self.name]
#        self.nwb.write_datasets(grp, "", self.spec)
#        from . import nwb as nwblib
#        nwblib.register_finalization(self.name, self.serial_num)


__interface_std_fields = ("help_statement",
                          "neurodata_type",
                          "source",
                          "interface")
@properties(*__interface_std_fields)
class Interface(Container):
    """ Interfaces represent particular processing tasks and they publish
        (ie, make available) specific types of data. Each is required
        to supply a minimum of specifically named data, but all can store 
        data beyond this minimum

        Interfaces should be created through Module.create_interface().
        They should not be created directly
    """

    _neurodata_type = "Interface"

    _interface = "Interface"

    _help_statement = None

    def __init__(self, source=None):
        #Arguments:
        #    *name* (text) name of interface (may be class name)
        #    *module* (*Module*) Reference to parent module object that 
        #       interface belongs to
        #    *spec* (dict) dictionary structure defining module specification
        #self.module = module
        #self.name = name
        #self.nwb = module.nwb
        #self.spec = copy.deepcopy(spec)
        ## timeseries that are added to interface directly
        #self.defined_timeseries = {}
        ## timeseries that exist elsewhere and are HDF5-linked
        #self.linked_timeseries = {}
        #if name in module.mod_folder:
        #    self.nwb.fatal_error("Interface %s already exists in module %s" % (name, module.name))
        #self.iface_folder = module.mod_folder.create_group(name)
        #self.serial_num = -1
        #self.finalized = False
        self._source = source
        self._timeseries = dict()

    def full_path(self):
        """ Returns HDF5 path to this interface

            Arguments:
                *none*

            Returns:
                (text) the HDF5 path to the interface
        """
        return "processing/" + self.module.name + "/" + self.name

    def create_timeseries(self, name, ts_type="TimeSeries"):
        ts_class = getattr(nwbts, ts_type, None)
        if not ts_class:
            raise ValueError("%s is an invalid TimeSeries type" % ts_type)
        self.timeseries[name] = ts_class(name)
        return self._timeseries[name]

    def add_timeseries(self, ts, name=None):
        """ Add a previously-defined *TimeSeries* to the interface. It will
            be added as an HDF5 link

            Arguments:
                *ts_name* (text) name of time series as it will appear in
                the interface

                *path* (text) path to the time series

            Returns:
                *nothing*
        """
        if name:
            self._timeseries[name] = ts
        else:
            self._timeseries[ts.name] = ts

    def get_timeseries(self):
        return timeseries

    def set_source(self, src):
        """ Identify source(s) for the data provided in the module.
            This can be one or more other modules, or time series
            in acquisition or stimulus

            Arguments:
                *src* (text) Path to objects providing data that the
                data here is based on

            Returns:
                *nothing*
        """
        self._source = src

class UnitTimes(Interface):

    iface_type = "UnitTimes"

    def __init__(self, name, module, spec):
        super(UnitTimes, self).__init__(name, module, spec)
        self.unit_list = []
    
    def add_unit(self, unit_name, unit_times, description, source):
        """ Adds data about a unit to the module, including unit name,
            description and times. 

            Arguments:
                *unit_name* (text) Name of the unit, as it will appear in the file

                *unit_times* (double array) Times that the unit spiked

                *description* (text) Information about the unit

                *source* (text) Name, path or description of where unit times originated
        """
        if unit_name not in self.iface_folder:
            self.iface_folder.create_group(unit_name)
        else:
            self.nwb.fatal_error("unit %s already exists" % unit_name)
        spec = copy.deepcopy(self.spec["<>"])
        spec["unit_description"]["_value"] = description
        spec["times"]["_value"] = unit_times
        spec["source"]["_value"] = source
        self.spec[unit_name] = spec
        #unit_times = ut.create_dataset("times", data=unit_times, dtype='f8')
        #ut.create_dataset("unit_description", data=description)
        self.unit_list.append(str(unit_name))

    def append_unit_data(self, unit_name, key, value):
        """ Add auxiliary information (key-value) about a unit.
            Data will be stored in the folder that contains data
            about that unit.

            Arguments:
                *unit_name* (text) Name of unit, as it appears in the file

                *key* (text) Key under which the data is added

                *value* (any) Data to be added

            Returns:
                *nothing*
        """
        if unit_name not in self.spec:
            self.nwb.fatal_error("unrecognized unit name " + unit_name)
        spec = copy.deepcopy(self.spec["<>"]["[]"])
        spec["_value"] = value
        self.spec[unit_name][key] = spec
        #ut.create_dataset(data_name, data=aux_data)

    def finalize(self):
        """ Extended (subclassed) finalize procedure. It creates and stores a list of all units in the module and then
            calls the superclass finalizer.

            Arguments:
                *none*

            Returns:
                *nothing*
        """
        if self.finalized:
            return
        self.spec["unit_list"]["_value"] = self.unit_list
        if len(self.unit_list) == 0:
            self.nwb.fatal_error("UnitTimes interface created with no units")
        super(UnitTimes, self).finalize()

########################################################################

class Clustering(Interface):

    iface_type = "Clustering"

    def set_clusters(self, times, num, peak_over_rms):
        """ Conveninece function to set interface values. Includes
            sanity checks for array lengths

            Arguments:
                *times* (double array) Times of clustered events, in
                seconds. This may be a link to times field in associated
                FeatureExtraction module. Array structure: [num events]

                *num* (int array) Cluster number for each event Array 
                structure: [num events]

                *description* (text)  Description of clusters or 
                clustering (e.g., cluster 0 is electrical noise, 
                clusters curated using Klusters, etc)

                *peak_over_rms* (float array) Maximum ratio of waveform 
                peak to RMS on any channel in the cluster (provides a 
                basic clustering metric).  Array structure: [num clusters]

            Returns:
                *nothing*
        """
        if len(times) != len(num):
            self.nwb.fatal_error("Time and cluster number arrays must be of equal length")
        if len(num) != len(peak_over_rms):
            self.nwb.fatal_error("Cluster number and peak/rms arrays must be of equal length")
        self.set_value("times", times)
        self.set_value("num", num)
        self.set_value("peak_over_rms", peak_over_rms)

    
    #BEGIN: AJTRITT code
    def add_event(self, cluster_num, time):
        self.nums.append(cluster_num)
        self.times.append(time)

    def add_cluster(self, cluster_num, peak_over_rms):
        self.peak_over_rms[cluster_num] = peak_over_rms
    #END: AJTRITT code

    def finalize(self):
        if self.finalized:
            return
        # make record of which cluster numbers are used
        # make sure clusters are present
        if "_value" not in self.spec["num"]:
            self.nwb.fatal_error("Clustering module %s has no clusters" % self.full_path())
        # now make a list of unique clusters and sort them
        num_dict = {}
        num = self.spec["num"]["_value"]
        for i in range(len(num)):
            n = "%d" % num[i]
            if n not in num_dict:
                num_dict[n] = n
        num_array = []
        for k in list(num_dict.keys()):
            num_array.append(int(k))
        num_array.sort()
        self.spec["cluster_nums"]["_value"] = num_array
        # continue with normal finalization
        super(Clustering, self).finalize()
    
########################################################################

class ImageSegmentation(Interface):

    iface_type = "ImageSegmentation"

    def __init__(self, name, module, spec):
        super(ImageSegmentation, self).__init__(name, module, spec)
        # make a table to store what ROIs are added to which planes
        self.roi_list = {}

    def add_reference_image(self, plane, name, img):
        """ Add a reference image to the segmentation interface

            Arguments: 
                *plane* (text) name of imaging plane

                *name* (text) name of reference image

                *img* (byte array) raw pixel map of image, 8-bit grayscale

            Returns:
                *nothing*
        """
        img_ts = self.nwb.create_timeseries("ImageSeries", name)
        img_ts.set_value("format", "raw")
        img_ts.set_value("bits_per_pixel", 8)
        img_ts.set_value("dimension", [len(img[0]), len(img)])
        img_ts.set_time([0])
        img_ts.set_data(img, "grayscale", 1, 1)
        img_ts.set_path(self.full_path() + "/" + plane + "/reference_images/")
        img_ts.finalize()

    def add_reference_image_as_link(self, plane, name, path):
        # make sure path is valid
        if path not in self.nwb.file_pointer:
            self.nwb.fatal_error("Path '%s' not found in file" % path)
        # make sure target is actually a time series
        if self.nwb.file_pointer[path].attrs["neurodata_type"] != "TimeSeries":
            self.nwb.fatal_error("'%s' is not a TimeSeries" % path)
        # make sure plane is present
        if plane not in self.iface_folder:
            self.nwb.fatal_error("'%s' is not a defined imaging plane in %s" % (plane, self.full_path()))
        # create link
        grp = self.iface_folder[plane]["reference_images"]
        grp[name] = self.nwb.file_pointer[path]

    def create_imaging_plane(self, plane, description):
    #def create_imaging_plane(self, plane, manifold, reference_frame, meta_link):
        ''' Defines imaging manifold. This can be a simple 1D or
            2D manifold, a complex 3D manifold, or even random
            access. The manifold defines the spatial coordinates for
            each pixel. If multi-planar manifolds are to be defined
            separately, a separate imaging plane should be used for each.
            Non-planar manifolds should be stored as a vector.
            
            Pixels in the manifold must have a 1:1 correspondence
            with image segmentation masks and the masks and manifold
            must have the same dimensions.
        '''
        if plane not in self.spec:
            self.spec[plane] = copy.deepcopy(self.spec["<>"])
        #self.spec[plane]["manifold"]["_value"] = manifold
        #self.spec[plane]["reference_frame"]["_value"] = reference_frame
        self.spec[plane]["imaging_plane_name"]["_value"] = plane
        self.spec[plane]["description"]["_value"] = description
        if plane in self.iface_folder:
            self.nwb.fatal_error("Imaging plane %s already exists" % plane)
        grp = self.iface_folder.create_group(plane)
        grp.create_group("reference_images")
        self.roi_list[plane] = []

    def add_roi_mask_pixels(self, image_plane, roi_name, desc, pixel_list, weights, width, height):
        """ Adds an ROI to the module, with the ROI defined using a list of pixels.

            Arguments:
                *image_plane* (text) name of imaging plane
            
                *roi_name* (text) name of ROI

                *desc* (text) description of ROI

                *pixel_list* (2D int array) array of [x,y] pixel values

                *weights* (float array) array of pixel weights (use None
                if all weights=1.0)

                *width* (int) width of reference image, in pixels

                *height* (int) height of reference image, in pixels

            Returns:
                *nothing*
        """
        # create image out of pixel list
        img = np.zeros((height, width), dtype=np.float32)
        if weights is None:
            weights = np.zeros(len(pixel_list)) + 1.0;
        for i in range(len(pixel_list)):
            img[pixel_list[i][1]][pixel_list[i][0]] = weights[i]
        self.add_masks(image_plane, roi_name, desc, pixel_list, weights, img)

    def add_roi_mask_img(self, image_plane, roi_name, desc, img):
        """ Adds an ROI to the module, with the ROI defined within a 2D image.

            Arguments:
                *image_plane* (text) name of imaging plane

                *roi_name* (text) name of ROI

                *desc* (text) description of ROI

                *img* (2D float array) description of ROI in a pixel map (float[y][x])

            Returns:
                *nothing*
        """
        # create pixel list out of image
        pixel_list = []
        weights = []
        for y in range(len(img)):
            row = img[y]
            for x in range(len(row)):
                if row[x] != 0:
                    pixel_list.append([x, y])
                    weights.append(row[x])
        self.add_masks(image_plane, roi_name, pixel_list, weights, img)

    # internal function
    def add_masks(self, plane, roi_name, desc, pixel_list, weights, img):
        if plane not in self.spec:
            self.nwb.fatal_error("Imaging plane %s not defined" % plane)
        if roi_name in self.spec[plane]:
            self.nwb.fatal_error("Imaging plane %s already has ROI %s" % (plane, roi_name))
        self.spec[plane][roi_name] = copy.deepcopy(self.spec["<>"]["<>"])
        self.spec[plane][roi_name]["pix_mask"]["_value"] = pixel_list
        self.spec[plane][roi_name]["pix_mask_weight"]["_value"] = weights
        #self.spec[plane][name]["pix_mask"]["_attributes"]["weight"]["_value"] = weights
        self.spec[plane][roi_name]["img_mask"]["_value"] = img
        self.spec[plane][roi_name]["roi_description"]["_value"] = desc
        self.roi_list[plane].append(roi_name)

    def finalize(self):
        if self.finalized:
            return
        # create roi_list for each plane
        for plane, roi_list in self.roi_list.items():
            self.spec[plane]["roi_list"]["_value"] = roi_list
        # continue with normal finalization
        super(ImageSegmentation, self).finalize()

########################################################################

class MotionCorrection(Interface):

    iface_type = "MotionCorrection"

    def add_corrected_image(self, name, orig, xy_translation, corrected):
        """ Adds a motion-corrected image to the module, including
            the original image stack, the x,y delta necessary to
            shift the image frames for registration, and the corrected
            image stack.
            NOTE 1: All 3 timeseries use the same timestamps and so can share/
            link timestamp arrays

            NOTE 2: The timeseries passed in as 'xy_translation' and
            'corrected' will be renamed to these names, if they are not
            links to existing timeseries

            NOTE 3: The timeseries arguments can be either TimeSeries
            objects (new or old in case of latter 2 args) or strings.
            If they are new TimeSeries objects, they will be stored
            within the module. If they are existing objects, a link
            to those objects will be created

            Arguments:
                *orig* (ImageSeries or text) ImageSeries object or
                text path to original image time series

                *xy_translation* TimeSeries storing displacements of
                x and y direction in the data[] field

                *corrected* Motion-corrected ImageSeries

            Returns:
                *nothing*
        """
        self.spec[name] = copy.deepcopy(self.spec["<>"])
        # create link to original object
        from . import nwbts
        if isinstance(orig, nwbts.TimeSeries):
            if not orig.finalized:
                self.nwb.fatal_error("Original timeseries must already be stored and finalized")
            orig_path = orig.full_path()
        else:
            orig_path = orig
        self.spec[name]["original"]["_value_hardlink"] = orig_path
        self.spec[name]["original_path"]["_value"] = orig_path
        links = "'original' is '%s'" % orig_path
        # finalize other time series, or create link if a string was
        #   provided
        # XY translation
        if isinstance(xy_translation, str):
            self.spec[name]["xy_translation"]["_value_hardlink"] = xy_translation
            links += "; 'xy_translation' is '%s'" % xy_translation
        else:
            if xy_translation.finalized:
                # timeseries exists in file -- link to it
                self.spec[name]["xy_translation"]["_value_hardlink"] = xy_translation.full_path()
                links += "; 'corrected' is '%s'" % xy_translation.full_path()
            else:
                # new timeseries -- set it's path and finalize it
                xy_translation.set_path("processing/" + self.module.name + "/MotionCorrection/" + name + "/")
                xy_translation.reset_name("xy_translation")
                xy_translation.finalize()
        # corrected series
        if isinstance(corrected, str):
            self.spec[name]["corrected"]["_value_hardlink"] = corrected
            links += "; 'corrected' is '%s'" % corrected
        else:
            if corrected.finalized:
                # timeseries exists in file -- link to it
                self.spec[name]["corrected"]["_value_hardlink"] = corrected.full_path()
                links += "; 'corrected' is '%s'" % corrected.full_path()
            else:
                corrected.set_path("processing/" + self.module.name + "/MotionCorrection/" + name + "/")
                corrected.reset_name("corrected")
                corrected.finalize()
        self.spec[name]["_attributes"]["links"]["_value"] = links

########################################################################

class ImagingRetinotopy(Interface):

    iface_type = "ImagingRetinotopy"

    def __init__(self, name, module, spec):
        super(ImagingRetinotopy, self).__init__(name, module, spec)
        # make a table to store what ROIs are added to which planes
        self.spec["axis_descriptions"]["_value"] = ["<undeclared>", "<undeclared>"]

    def add_axis_1_phase_map(self, response, axis_name, width, height, unit="degrees"):
        """ Adds calculated response along first measured axes

            Arguments:
                *response* (2D int array) Calculated phase response to 
                stimulus on the first measured axis

                *axis_name* (text) Description of axis (e.g., "altitude", 
                "azimuth", "radius", or "theta")

                *width* (float) Field of view width, in meters

                *height* (float) Field of view height, in meters

                *unit* (text) SI unit of data

            Returns:
                *nothing*
        """
        self.spec["axis_1_phase_map"]["_value"] = response
        self.spec["axis_1_phase_map"]["_attributes"]["unit"]["_value"] = unit
        self.spec["axis_1_phase_map"]["_attributes"]["field_of_view"]["_value"] = [height, width]
        self.spec["axis_descriptions"]["_value"][0] = axis_name
        try:
            dim1 = len(response)
            dim2 = len(response[0])
            if dim1 == 0 or dim2 == 0:
                self.nwb.fatal_error("Invalid image dimensions for axis_1")
        except:
            self.nwb.fatal_error("Error calculating image dimensions for axis_1")
        self.spec["axis_1_phase_map"]["_attributes"]["dimension"]["_value"] = [dim1, dim2]

    def add_axis_1_power_map(self, power_map, width=None, height=None):
        """ Adds power of response along first measured axes

            Arguments:
                *power_map* (2D int array) Calculated power response to 
                stimulus on the first measured axis. All values in power
                map should be on the interval [0, 1]

                *width* (float) Field of view width, in meters

                *height* (float) Field of view height, in meters

            Returns:
                *nothing*
        """
        if power_map is None:    # ignore empty requests
            return
        if np.max(power_map) > 1.0 or np.min(power_map) < 0.0:
            self.nwb.fatal_error("Power map requires relative power values, on the range >=0 and <=1.0")
        self.spec["axis_1_power_map"]["_value"] = power_map
        if height is not None and width is not None:
            self.spec["axis_1_power_map"]["_attributes"]["field_of_view"]["_value"] = [height, width]
        elif height is not None or width is not None:
            self.nwb.fatal_error("Must specify both width and height if specifying either")
        try:
            dim1 = len(power_map)
            dim2 = len(power_map[0])
            if dim1 == 0 or dim2 == 0:
                self.nwb.fatal_error("Invalid image dimensions for axis_1")
        except:
            self.nwb.fatal_error("Error calculating image dimensions for axis_1")
        self.spec["axis_1_power_map"]["_attributes"]["dimension"]["_value"] = [dim1, dim2]

    def add_axis_2_phase_map(self, response, axis_name, width, height, unit="degrees"):
        """ Adds calculated response along one of two measured axes

            Arguments:
                *response* (2D int array) Calculated phase response to 
                stimulus on the second measured axis

                *axis_name* (text) Description of axis (e.g., "altitude", 
                "azimuth", "radius", or "theta")

                *unit* (text) SI unit of data

            Returns:
                *nothing*
        """
        self.spec["axis_2_phase_map"]["_value"] = response
        self.spec["axis_2_phase_map"]["_attributes"]["unit"]["_value"] = unit
        self.spec["axis_2_phase_map"]["_attributes"]["field_of_view"]["_value"] = [height, width]
        self.spec["axis_descriptions"]["_value"][1] = axis_name
        try:
            dim1 = len(response)
            dim2 = len(response[0])
            if dim1 == 0 or dim2 == 0:
                self.nwb.fatal_error("Invalid image dimensions for axis_2")
        except:
            self.nwb.fatal_error("Error calculating image dimensions for axis_2")
        self.spec["axis_2_phase_map"]["_attributes"]["dimension"]["_value"] = [dim1, dim2]

    def add_axis_2_power_map(self, power_map, width=None, height=None):
        """ Adds power of response along second measured axes

            Arguments:
                *power_map* (2D int array) Calculated power response to 
                stimulus on the second measured axis. All values in power
                map should be on the interval [0, 1]

                *width* (float) Field of view width, in meters

                *height* (float) Field of view height, in meters

            Returns:
                *nothing*
        """
        if power_map is None:    # ignore empty requests
            return
        if np.max(power_map) > 1.0 or np.min(power_map) < 0.0:
            self.nwb.fatal_error("Power map requires relative power values, on the range >=0 and <=1.0")
        self.spec["axis_2_power_map"]["_value"] = power_map
        if height is not None and width is not None:
            self.spec["axis_2_power_map"]["_attributes"]["field_of_view"]["_value"] = [height, width]
        elif height is not None or width is not None:
            self.nwb.fatal_error("Must specify both width and height if specifying either")
        try:
            dim1 = len(power_map)
            dim2 = len(power_map[0])
            if dim1 == 0 or dim2 == 0:
                self.nwb.fatal_error("Invalid image dimensions for axis_2")
        except:
            self.nwb.fatal_error("Error calculating image dimensions for axis_2")
        self.spec["axis_2_power_map"]["_attributes"]["dimension"]["_value"] = [dim1, dim2]

    def add_sign_map(self, sign_map, width=None, height=None):
        """ Adds sign (polarity) map to module

            Arguments:
                *sign_map* (2D float array) sine of the angle between the 
                direction of the gradient in axis_1 and axis_2

                *width* (float) Field of view width, in meters

                *height* (float) Field of view height, in meters

            Returns:
                *nothing*
        """
        self.spec["sign_map"]["_value"] = sign_map
        try:
            dim1 = len(sign_map)
            dim2 = len(sign_map[0])
            if dim1 == 0 or dim2 == 0:
                self.nwb.fatal_error("Invalid image dimensions for sign map")
        except:
            self.nwb.fatal_error("Error calculating image dimensions for sign map")
        if height is not None and width is not None:
            self.spec["sign_map"]["_attributes"]["field_of_view"]["_value"] = [height, width]
        elif height is not None or width is not None:
            self.nwb.fatal_error("Must specify both width and height if specifying either")
        self.spec["sign_map"]["_attributes"]["dimension"]["_value"] = [dim1, dim2]

    def internal_add_image(self, name, img, width, height, bpp):
        if bpp is None:
            bpp = int(math.log(np.max(img), 2) + 1.0)
        try:
            dim1 = len(img)
            dim2 = len(img[0])
            if dim1 == 0 or dim2 == 0:
                self.nwb.fatal_error("Invalid image dimensions for " + name)
        except:
            self.nwb.fatal_error("Error calculating image dimensions for " + name)
        if height is not None and width is not None:
            self.spec[name]["_attributes"]["field_of_view"]["_value"] = [height, width]
        elif height is not None or width is not None:
            self.nwb.fatal_error("Must specify both width and height if specifying either")
        self.spec[name]["_value"] = img
        self.spec[name]["_attributes"]["bits_per_pixel"]["_value"] = bpp
        self.spec[name]["_attributes"]["dimension"]["_value"] = [dim1, dim2]

    def add_vasculature_image(self, img, width=None, height=None, bpp=None):
        """ Anatomical image showing vasculature and cortical surface

            Arguments:
                *img* (2D float array) Gray-scale anatomical image 
                of cortical surface. Array structure: [rows][columns]

                *width* (float) Field of view width, in meters

                *height* (float) Field of view height, in meters

                *bpp* (int) Bits per pixel. This is necessary to determine
                pixel value for "white". If no value is supplied, a 
                calculation is performed to infer one

            Returns:
                *nothing*
        """
        self.internal_add_image("vasculature_image", img, width, height, bpp)

    def add_focal_depth_image(self, img, depth=None, width=None, height=None, bpp=None):
        """ Adds "defocused" image taken at depth of imaging plane, using
            same settings/parameters as acquired data (eg, wavelength,
            depth)

            Arguments:
                *img* (2D float array) Gray-scale image taken with same 
                settings/parameters as data collection. 
                Array format: [rows][columns]

                *depth* (float) Depth of imaging plane below surface 

                *width* (float) Field of view width, in meters

                *height* (float) Field of view height, in meters

                *bpp* (int) Bits per pixel. This is necessary to determine
                pixel value for "white". If no value is supplied, a 
                calculation is performed to infer one

            Returns:
                *nothing*
        """
        self.internal_add_image("focal_depth_image", img, width, height, bpp)
        if depth is not None:
            self.spec["focal_depth_image"]["_attributes"]["focal_depth"]["_value"] = depth

