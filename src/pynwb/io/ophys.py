from hdmf.common.io.table import DynamicTableMap

from .core import NWBContainerMapper
from ..ophys import PlaneSegmentation, ImagingPlane
from ..tools import register_map


@register_map(PlaneSegmentation)
class PlaneSegmentationMap(DynamicTableMap):

    def __init__(self, spec):
        super().__init__(spec)

        reference_images_spec = self.spec.get_group('reference_images').get_neurodata_type('ImageSeries')
        self.map_spec('reference_images', reference_images_spec)


@register_map(ImagingPlane)
class ImagingPlaneMap(NWBContainerMapper):

    def __init__(self, spec):
        super().__init__(spec)
        manifold_spec = self.spec.get_dataset('manifold')
        origin_coords_spec = self.spec.get_dataset('origin_coords')
        grid_spacing_spec = self.spec.get_dataset('grid_spacing')
        self.map_spec('unit', manifold_spec.get_attribute('unit'))
        self.map_spec('conversion', manifold_spec.get_attribute('conversion'))
        self.map_spec('origin_coords_unit', origin_coords_spec.get_attribute('unit'))
        self.map_spec('grid_spacing_unit', grid_spacing_spec.get_attribute('unit'))
        self.map_spec('optical_channel', self.spec.get_neurodata_type('OpticalChannel'))
