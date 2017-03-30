from .core import docval, popargs
from .base import Interface

from collections import Iterable


class ImageRetinotopy(Interface):
    """
    Intrinsic signal optical imaging or widefield imaging for measuring retinotopy. Stores orthogonal
    maps (e.g., altitude/azimuth; radius/theta) of responses to specific stimuli and a combined
    polarity map from which to identify visual areas.
    Note: for data consistency, all images and arrays are stored in the format [row][column] and
    [row, col], which equates to [y][x]. Field of view and dimension arrays may appear backward
    (i.e., y before x).
    """

    __nwbfields__ = ('axis_1_phase_map',
                     'axis_1_power_map',
                     'axis_2_phase_map',
                     'axis_2_power_map',
                     'axis_descriptions',
                     'focal_depth_image',
                     'sign_map',
                     'vasculature_image',)

    _help = "Intrinsic signal optical imaging or Widefield imaging for measuring retinotopy."

    @docval({'name': 'source', 'type': str, 'doc': 'the source of the data represented in this Module Interface'},
            {'name': 'axis_1_phase_map', 'type': Iterable, 'doc': ''},
            {'name': 'axis_1_power_map', 'type': Iterable, 'doc': ''},
            {'name': 'axis_2_phase_map', 'type': Iterable, 'doc': ''},
            {'name': 'axis_2_power_map', 'type': Iterable, 'doc': ''},
            {'name': 'axis_descriptions', 'type': Iterable, 'doc': ''},
            {'name': 'focal_depth_image', 'type': Iterable, 'doc': ''},
            {'name': 'sign_map', 'type': Iterable, 'doc': ''},
            {'name': 'vasculature_image', 'type': Iterable, 'doc': ''})
    def __init__(self, **kwargs):
        source, axis_1_phase_map, axis_1_power_map, axis_2_phase_map, axis_2_power_map, axis_descriptions, focal_depth_image, sign_map, vasculature_image = popargs('source', 'axis_1_phase_map', 'axis_1_power_map', 'axis_2_phase_map', 'axis_2_power_map', 'axis_descriptions', 'focal_depth_image', 'sign_map', 'vasculature_image', kwargs)
        super(ImageRetinotopy, self).__init__(source, **kwargs)
        self.axis_1_phase_map = axis_1_phase_map
        self.axis_1_power_map = axis_1_power_map
        self.axis_2_phase_map = axis_2_phase_map
        self.axis_2_power_map = axis_2_power_map
        self.axis_descriptions = axis_descriptions
        self.focal_depth_image = focal_depth_image
        self.sign_map = sign_map
        self.vasculature_image = vasculature_image

