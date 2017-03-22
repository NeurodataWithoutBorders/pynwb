from .base import TimeSeries

class ImageSeries(TimeSeries):
    pass

class IndexSeries(TimeSeries):
    pass

class ImageMaskSeries(ImageSeries):
    pass

class OpticalSeries(ImageSeries):
    pass

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
        if isinstance(orig, _timeseries.TimeSeries):
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
