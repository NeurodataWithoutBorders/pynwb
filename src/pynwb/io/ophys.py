from ..form.build import ObjectMapper
from .. import register_map

from ..ophys import PlaneSegmentation, ROITable, ROITableRegion
from .core import NWBDataMap, NWBTableRegionMap


@register_map(PlaneSegmentation)
class PlaneSegmentationMap(ObjectMapper):

    # This might be needed for 2.0 as well
    def __init__(self, spec):
        super(PlaneSegmentationMap, self).__init__(spec)

        reference_images_spec = self.spec.get_group('reference_images').get_neurodata_type('ImageSeries')
        self.map_spec('reference_images', reference_images_spec)


@register_map(ROITable)
class ROITableMap(NWBDataMap):
    def __init__(self, spec):
        super(ROITableMap, self).__init__(spec)


@register_map(ROITableRegion)
class ROITableRegionMap(NWBTableRegionMap):
    pass
