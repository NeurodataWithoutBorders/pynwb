from collections import Iterable

from form.utils import docval, popargs

from .base import Interface

#@register_class('ImageRetinotopy', CORE_NAMESPACE)    # make sure to uncomment this after this class is implemented
class ImageRetinotopy(Interface):
    """
    """

    __nwbfields__ = ('data',
                     'bits_per_pixel',
                     'dimension',
                     'format',
                     'field_of_view',
                     'focal_depth')

    @docval({'name': 'data', 'type': Iterable, 'doc': 'Data field.'},
            {'name': 'bits_per_pixel', 'type': int, 'doc': 'Number of bits used to represent each value. This is necessary to determine maximum (white) pixel value.'},
            {'name': 'dimension', 'type': Iterable, 'doc': 'Number of rows and columns in the image.'},
            {'name': 'format', 'type': Iterable, 'doc': 'Format of image. Right now only "raw" supported.'},
            {'name': 'field_of_view', 'type': Iterable, 'doc': 'Size of viewing area, in meters.'},
            {'name': 'focal_depth', 'type': float, 'doc': 'Focal depth offset, in meters.'})
    def __init__(self, **kwargs):
        data, bits_per_pixel, dimension, format, field_of_view = popargs('data', 'bits_per_pixel', 'dimension', 'format', 'field_of_view', kwargs)
        super(aimage, self).__init__(**kwargs)
        self.data = data
        self.bits_per_pixel = bits_per_pixel
        self.dimension = format
        self.field_of_view = field_of_view

class amap(NWBContainer):
    """
    """

    __nwbfields__ = ('data',
                     'field_of_view',
                     'unit',
                     'dimension')

    @docval({'name': 'data', 'type': Iterable, 'doc': 'data field.'},
            {'name': 'field_of_view', 'type': Iterable, 'doc': 'Size of viewing area, in meters.'},
            {'name': 'unit', 'type': str, 'doc': 'Unit that axis data is stored in (e.g., degrees)'},
            {'name': 'dimension', 'type': Iterable, 'doc': 'Number of rows and columns in the image'})
    def __init__(self, **kwargs):
        data, field_of_view, unit, dimension = popargs('data', 'field_of_view', 'unit', 'dimension', kwargs)
        super(amap, self).__init__(**kwargs)
        self.data = data
        self.field_of_view = field_of_view
        self.unit = unit
        self.dimension = dimension

class ImagingRetinotopy(Interface):
>>>>>>> dev
    """
    Intrinsic signal optical imaging or widefield imaging for measuring retinotopy. Stores orthogonal
    maps (e.g., altitude/azimuth; radius/theta) of responses to specific stimuli and a combined
    polarity map from which to identify visual areas.
    Note: for data consistency, all images and arrays are stored in the format [row][column] and
    [row, col], which equates to [y][x]. Field of view and dimension arrays may appear backward
    (i.e., y before x).
    """

    __nwbfields__ = ('sign_map',
                     'axis_1_phase_map',
                     'axis_1_power_map',
                     'axis_2_phase_map',
                     'axis_2_power_map',
                     'axis_descriptions',
                     'focal_depth_image',
                     'vasculature_image',)

    _help = "Intrinsic signal optical imaging or Widefield imaging for measuring retinotopy."

    @docval({'name': 'source', 'type': str, 'doc': 'The source of the data represented in this Module Interface.'},
            {'name': 'sign_map', 'type': amap, 'doc': 'Sine of the angle between the direction of the gradient in axis_1 and axis_2.'},
            {'name': 'axis_1_phase_map', 'type': amap, 'doc': 'Phase response to stimulus on the first measured axis.'},
            {'name': 'axis_1_power_map', 'type': amap, 'doc': 'Power response on the first measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.'},
            {'name': 'axis_2_phase_map', 'type': amap, 'doc': 'Phase response to stimulus on the second measured axis.'},
            {'name': 'axis_2_power_map', 'type': amap, 'doc': 'Power response on the second measured axis. Response is scaled so 0.0 is no power in the response and 1.0 is maximum relative power.'},
            {'name': 'axis_descriptions', 'type': Iterable, 'doc': 'Two-element array describing the contents of the two response axis fields. Description should be something like ["altitude", "azimuth"] or ["radius", "theta"].'},
            {'name': 'focal_depth_image', 'type': aimage, 'doc': 'Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) as data collection. Array format: [rows][columns].'},
            {'name': 'vasculature_image', 'type': aimage, 'doc': 'Gray-scale anatomical image of cortical surface. Array structure: [rows][columns].'})
    def __init__(self, **kwargs):
        source, axis_1_phase_map, axis_1_power_map, axis_2_phase_map, axis_2_power_map, axis_descriptions, focal_depth_image, sign_map, vasculature_image = popargs('source', 'axis_1_phase_map', 'axis_1_power_map', 'axis_2_phase_map', 'axis_2_power_map', 'axis_descriptions', 'focal_depth_image', 'sign_map', 'vasculature_image', kwargs)
        super(ImagingRetinotopy, self).__init__(source, **kwargs)
        self.axis_1_phase_map = axis_1_phase_map
        self.axis_1_power_map = axis_1_power_map
        self.axis_2_phase_map = axis_2_phase_map
        self.axis_2_power_map = axis_2_power_map
        self.axis_descriptions = axis_descriptions
        self.focal_depth_image = focal_depth_image
        self.sign_map = sign_map
        self.vasculature_image = vasculature_image

