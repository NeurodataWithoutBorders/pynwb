from .image import ImageSeries
from .core import docval, getargs, NWBContainer
from .base import Interface

class TwoPhotonSeries(ImageSeries):
    pass

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
