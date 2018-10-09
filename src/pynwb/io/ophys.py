from .. import register_map

from ..ophys import PlaneSegmentation
from .core import DynamicTableMap


@register_map(PlaneSegmentation)
class PlaneSegmentationMap(DynamicTableMap):

    # This might be needed for 2.0 as well
    def __init__(self, spec):
        super(PlaneSegmentationMap, self).__init__(spec)

        reference_images_spec = self.spec.get_group('reference_images').get_neurodata_type('ImageSeries')
        self.map_spec('reference_images', reference_images_spec)
