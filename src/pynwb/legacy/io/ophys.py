from .. import ObjectMapper
from pynwb.legacy import register_map
from pynwb.ophys import PlaneSegmentation

@register_map(PlaneSegmentation)
class PlaneSegmentationMap(ObjectMapper):

    @ObjectMapper.constructor_arg('roi_list')
    def carg_roi_list(self, builder):
        return builder.get('rois')

    @ObjectMapper.constructor_arg('imaging_plane')
    def carg_imaging_plane(self, builder):
        return builder.get('imaging_plane')

    @ObjectMapper.constructor_arg('reference_images')
    def carg_reference_images(self, builder):
        return builder.get('reference_images')
