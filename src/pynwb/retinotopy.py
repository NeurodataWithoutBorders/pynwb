
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

