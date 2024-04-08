raise ImportError(
    "The pynwb.retinotopy module is deprecated. If you are interested in using these neurodata types, "
    "please create an issue on https://github.com/NeurodataWithoutBorders/nwb-schema/issues."
)

# import warnings
# from collections.abc import Iterable

# from hdmf.utils import docval, popargs, get_docval

# from . import register_class, CORE_NAMESPACE
# from .core import NWBDataInterface, NWBData


# class RetinotopyImage(NWBData):
#     """Gray-scale anatomical image of cortical surface. Array structure: [rows][columns]
#     """

#     __nwbfields__ = ('bits_per_pixel',
#                      'dimension',
#                      'format',
#                      'field_of_view')

#     @docval({'name': 'name', 'type': str, 'doc': 'Name of this retinotopy image'},
#             {'name': 'data', 'type': Iterable, 'doc': 'Data field.'},
#             {'name': 'bits_per_pixel', 'type': int,
#              'doc': 'Number of bits used to represent each value. This is necessary to determine maximum '
#                     '(white) pixel value.'},
#             {'name': 'dimension', 'type': Iterable, 'shape': (2, ),
#              'doc': 'Number of rows and columns in the image.'},
#             {'name': 'format', 'type': Iterable, 'doc': 'Format of image. Right now only "raw" supported.'},
#             {'name': 'field_of_view', 'type': Iterable, 'shape': (2, ), 'doc': 'Size of viewing area, in meters.'})
#     def __init__(self, **kwargs):
#         bits_per_pixel, dimension, format, field_of_view = popargs(
#             'bits_per_pixel', 'dimension', 'format', 'field_of_view', kwargs)
#         super().__init__(**kwargs)
#         self.bits_per_pixel = bits_per_pixel
#         self.dimension = dimension
#         self.format = format
#         self.field_of_view = field_of_view


# class FocalDepthImage(RetinotopyImage):
#     """Gray-scale image taken with same settings/parameters (e.g., focal depth,
#     wavelength) as data collection. Array format: [rows][columns].
#     """

#     __nwbfields__ = ('focal_depth', )

#     @docval(*get_docval(RetinotopyImage.__init__),
#             {'name': 'focal_depth', 'type': float, 'doc': 'Focal depth offset, in meters.'})
#     def __init__(self, **kwargs):
#         focal_depth = popargs('focal_depth', kwargs)
#         super().__init__(**kwargs)
#         self.focal_depth = focal_depth


# class RetinotopyMap(NWBData):
#     """Abstract two-dimensional map of responses to stimuli along a single response axis (e.g., altitude)
#     """

#     __nwbfields__ = ('field_of_view',
#                      'dimension')

#     @docval({'name': 'name', 'type': str, 'doc': 'the name of this axis map'},
#             {'name': 'data', 'type': Iterable, 'shape': (None, None), 'doc': 'data field.'},
#             {'name': 'field_of_view', 'type': Iterable, 'shape': (2, ), 'doc': 'Size of viewing area, in meters.'},
#             {'name': 'dimension', 'type': Iterable, 'shape': (2, ),
#              'doc': 'Number of rows and columns in the image'})
#     def __init__(self, **kwargs):
#         field_of_view, dimension = popargs('field_of_view', 'dimension', kwargs)
#         super().__init__(**kwargs)
#         self.field_of_view = field_of_view
#         self.dimension = dimension


# class AxisMap(RetinotopyMap):
#     """Abstract two-dimensional map of responses to stimuli along a single response axis (e.g., altitude) with unit
#     """

#     __nwbfields__ = ('unit', )

#     @docval(*get_docval(RetinotopyMap.__init__, 'name', 'data', 'field_of_view'),
#             {'name': 'unit', 'type': str, 'doc': 'Unit that axis data is stored in (e.g., degrees)'},
#             *get_docval(RetinotopyMap.__init__, 'dimension'))
#     def __init__(self, **kwargs):
#         unit = popargs('unit', kwargs)
#         super().__init__(**kwargs)
#         self.unit = unit


# @register_class('ImagingRetinotopy', CORE_NAMESPACE)
# class ImagingRetinotopy(NWBDataInterface):
#     """
#     Intrinsic signal optical imaging or widefield imaging for measuring retinotopy. Stores orthogonal
#     maps (e.g., altitude/azimuth; radius/theta) of responses to specific stimuli and a combined
#     polarity map from which to identify visual areas.
#     This group does not store the raw responses imaged during retinotopic mapping or the
#     stimuli presented, but rather the resulting phase and power maps after applying a Fourier
#     transform on the averaged responses.
#     Note: for data consistency, all images and arrays are stored in the format [row][column] and
#     [row, col], which equates to [y][x]. Field of view and dimension arrays may appear backward
#     (i.e., y before x).
#     """

#     __nwbfields__ = ({'name': 'sign_map', 'child': True},
#                      {'name': 'axis_1_phase_map', 'child': True},
#                      {'name': 'axis_1_power_map', 'child': True},
#                      {'name': 'axis_2_phase_map', 'child': True},
#                      {'name': 'axis_2_power_map', 'child': True},
#                      {'name': 'focal_depth_image', 'child': True},
#                      {'name': 'vasculature_image', 'child': True},
#                      'axis_descriptions')

#     @docval({'name': 'sign_map', 'type': RetinotopyMap,
#              'doc': 'Sine of the angle between the direction of the gradient in axis_1 and axis_2.'},
#             {'name': 'axis_1_phase_map', 'type': AxisMap,
#              'doc': 'Phase response to stimulus on the first measured axis.'},
#             {'name': 'axis_1_power_map', 'type': AxisMap,
#              'doc': 'Power response on the first measured axis. Response is scaled so 0.0 is no power in '
#                     'the response and 1.0 is maximum relative power.'},
#             {'name': 'axis_2_phase_map', 'type': AxisMap,
#              'doc': 'Phase response to stimulus on the second measured axis.'},
#             {'name': 'axis_2_power_map', 'type': AxisMap,
#              'doc': 'Power response on the second measured axis. Response is scaled so 0.0 is no '
#                      'power in the response and 1.0 is maximum relative power.'},
#             {'name': 'axis_descriptions', 'type': Iterable, 'shape': (2, ),
#              'doc': 'Two-element array describing the contents of the two response axis fields. '
#                     'Description should be something like ["altitude", "azimuth"] or ["radius", "theta"].'},
#             {'name': 'focal_depth_image', 'type': FocalDepthImage,
#              'doc': 'Gray-scale image taken with same settings/parameters (e.g., focal depth, wavelength) '
#                     'as data collection. Array format - [rows][columns].'},
#             {'name': 'vasculature_image', 'type': RetinotopyImage,
#              'doc': 'Gray-scale anatomical image of cortical surface. Array structure - [rows][columns].'},
#             {'name': 'name', 'type': str, 'doc': 'the name of this container', 'default': 'ImagingRetinotopy'})
#     def __init__(self, **kwargs):
#         axis_1_phase_map, axis_1_power_map, axis_2_phase_map, axis_2_power_map, axis_descriptions, \
#             focal_depth_image, sign_map, vasculature_image = popargs(
#                 'axis_1_phase_map', 'axis_1_power_map', 'axis_2_phase_map', 'axis_2_power_map',
#                 'axis_descriptions', 'focal_depth_image', 'sign_map', 'vasculature_image', kwargs)
#         super().__init__(**kwargs)
#         warnings.warn("The ImagingRetinotopy class currently cannot be written to or read from a file. "
#                       "This is a known bug and will be fixed in a future release of PyNWB.")
#         self.axis_1_phase_map = axis_1_phase_map
#         self.axis_1_power_map = axis_1_power_map
#         self.axis_2_phase_map = axis_2_phase_map
#         self.axis_2_power_map = axis_2_power_map
#         self.axis_descriptions = axis_descriptions
#         self.focal_depth_image = focal_depth_image
#         self.sign_map = sign_map
#         self.vasculature_image = vasculature_image
