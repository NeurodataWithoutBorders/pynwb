from .image import ImageSeries
from .core import docval, getargs, popargs, NWBContainer
from .base import Interface

class TwoPhotonSeries(ImageSeries):
    '''
    A special case of optical imaging.
    '''

    __nwbfields__ = ('field_of_view',
                     'imaging_plane',
                     'pmt_gain',
                     'scan_line_rate')

    _ancestry = "TimeSeries,ImageSeries,TwoPhotonSeries"
    _help = "Image stack recorded from 2-photon microscope."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'field_of_view', 'type': (list, np.ndarray, 'TimeSeries'), 'doc': 'Width, height and depth of image, or imaged area (meters).'},
            {'name': 'imaging_plane', 'type': str, 'doc': 'Name of imaging plane description in /general/optophysiology.'},
            {'name': 'pmt_gain', 'type': float, 'doc': 'Photomultiplier gain.'},
            {'name': 'scan_line_rate', 'type': float, 'doc': 'Lines imaged per second. This is also stored in /general/optophysiology but is kept here as it is useful information for analysis, and so good to be stored w/ the actual data.'},

            {'name': 'external_file', 'type': Iterable, 'doc': 'Path or URL to one or more external file(s). Field only present if format=external. Either external_file or data must be specified, but not both.'},
            {'name': 'starting_frame', 'type': Iterable, 'doc': 'Each entry is the frame number in the corresponding external_file variable. This serves as an index to what frames each file contains.'},
            {'name': 'format', 'type': str, 'doc': 'Format of image. Three types: 1) Image format; tiff, png, jpg, etc. 2) external 3) raw.'},
            {'name': 'bits_per_pixel', 'type': float, 'doc': 'Number of bit per image pixel', 'default': np.nan},
            {'name': 'dimension', 'type': Iterable, 'doc': 'Number of pixels on x, y, (and z) axes.', 'default': [np.nan]},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit, external_file, starting_frame, format = popargs('name', 'source', 'data', 'unit', 'external_file', 'starting_frame', 'format', kwargs)
        field_of_view, imaging_plane, pmt_gain, scan_line_rate = popargs('field_of_view', 'imaging_plane', 'pmt_gain', 'scan_line_rate', kwargs)
        super(TwoPhotonSeries, self).__init__(name, source, data, unit, external_file, starting_frame, format, **kwargs)
        self.field_of_view = field_of_view
        self.imaging_plane = imaging_plane
        self.pmt_gain = pmt_gain
        self.scan_line_rate = scan_line_rate

class RoiResponseSeries(TimeSeries):
    '''
    ROI responses over an imaging plane. Each row in data[] should correspond to the signal from one ROI.
    '''

    __nwbfields__ = ('roi_names',
                     'segmenttation_interface',
                     'segmenttation_interface_path')

    _ancestry = "TimeSeries,ImageSeries,ImageMaskSeries"
    _help = "ROI responses over an imaging plane. Each row in data[] should correspond to the signal from one no ROI."

    @docval({'name': 'name', 'type': str, 'doc': 'The name of this TimeSeries dataset'},
            {'name': 'source', 'type': str, 'doc': ('Name of TimeSeries or Modules that serve as the source for the data '
                                                   'contained here. It can also be the name of a device, for stimulus or '
                                                   'acquisition data')},
            {'name': 'data', 'type': (list, np.ndarray, TimeSeries), 'doc': 'The data this TimeSeries dataset stores. Can also store binary data e.g. image frames'},
            {'name': 'unit', 'type': str, 'doc': 'The base unit of measurement (should be SI unit)'},

            {'name': 'roi_names', 'type': Iterable, 'doc': 'List of ROIs represented, one name for each row of data[].'},
            {'name': 'segmenttation_interface', 'type': ImageSeries, 'doc': 'Link to ImageSeries that mask is applied to.'},
            {'name': 'segmenttation_interface_path', 'type': str, 'doc': 'Path to linked ImageSeries.'},

            {'name': 'resolution', 'type': float, 'doc': 'The smallest meaningful difference (in specified unit) between values in data', 'default': _default_resolution},
            {'name': 'conversion', 'type': float, 'doc': 'Scalar to multiply each element by to conver to volts', 'default': _default_conversion},

            {'name': 'timestamps', 'type': (list, np.ndarray, TimeSeries), 'doc': 'Timestamps for samples stored in data', 'default': None},
            {'name': 'starting_time', 'type': float, 'doc': 'The timestamp of the first sample', 'default': None},
            {'name': 'rate', 'type': float, 'doc': 'Sampling rate in Hz', 'default': None},

            {'name': 'comments', 'type': str, 'doc': 'Human-readable comments about this TimeSeries dataset', 'default':None},
            {'name': 'description', 'type': str, 'doc': 'Description of this TimeSeries dataset', 'default':None},
            {'name': 'control', 'type': Iterable, 'doc': 'Numerical labels that apply to each element in data', 'default': None},
            {'name': 'control_description', 'type': Iterable, 'doc': 'Description of each control value', 'default': None},
            {'name': 'parent', 'type': 'NWBContainer', 'doc': 'The parent NWBContainer for this NWBContainer', 'default': None},
    )
    def __init__(self, **kwargs):
        name, source, data, unit = popargs('name', 'source', 'data', 'unit', kwargs)
        roi_names, segmenttation_interface, segmenttation_interface_path = popargs('roi_names', 'segmenttation_interface', 'segmenttation_interface_path', kwargs)
        super(RoiResponseSeries, self).__init__(name, source, data, unit, **kwargs)
        self.roi_names = roi_names
        self.segmenttation_interface = segmenttation_interface
        self.segmenttation_interface_path = segmenttation_interface_path

class DfOverF(Interface):
    pass

class Fluorescence(Interface):
    pass

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


class ImagingPlane(NWBContainer):
    # see /general/optophysiology/<imaging_plane_X> spec
    pass

class OpticalChannel(NWBContainer):
    # see /general/optophysiology/<imaging_plane_X>/<channel_X> spec
    pass
