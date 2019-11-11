from .. import register_map

from ..ophys import PlaneSegmentation, ImagingPlane
from .core import NWBContainerMapper
from hdmf.common.io.table import DynamicTableMap


@register_map(PlaneSegmentation)
class PlaneSegmentationMap(DynamicTableMap):

    def __init__(self, spec):
        super(PlaneSegmentationMap, self).__init__(spec)

        reference_images_spec = self.spec.get_group('reference_images').get_neurodata_type('ImageSeries')
        self.map_spec('reference_images', reference_images_spec)


@register_map(ImagingPlane)
class ImagingPlaneMap(NWBContainerMapper):

    def __init__(self, spec):
        super(ImagingPlaneMap, self).__init__(spec)
        manifold_spec = self.spec.get_dataset('manifold')
        self.map_spec('unit', manifold_spec.get_attribute('unit'))
        self.map_spec('conversion', manifold_spec.get_attribute('conversion'))
