from .. import ObjectMapper
from pynwb.legacy import register_map
from pynwb.ophys import PlaneSegmentation, ROI

@register_map(PlaneSegmentation)
class PlaneSegmentationMap(ObjectMapper):

    def __init__(self, spec):
        super(PlaneSegmentationMap, self).__init__(spec)
        roi_spec = self.spec.get_neurodata_type('ROI')
        self.map_const_arg('roi_list', roi_spec)

        reference_images_spec = self.spec.get_neurodata_type('ImageSeries')
        self.map_const_arg('reference_images', reference_images_spec)

    # @ObjectMapper.constructor_arg('roi_list')
    # def carg_roi_list(self, builder):
    #     return builder.get('rois')

    @ObjectMapper.constructor_arg('imaging_plane')
    def carg_imaging_plane(self, builder):
        return 'imaging_plane_1' #builder.get('imaging_plane')

    # @ObjectMapper.constructor_arg('reference_images')
    # def carg_reference_images(self, builder):
    #     return builder.get('image_series') # builder.get('reference_images')

    # @ObjectMapper.constructor_arg('reference_images')
    # def carg_reference_images(self, builder):
    #     return builder.get('image_series') # builder.get('reference_images')


@register_map(ROI)
class ROIMap(ObjectMapper):

    @ObjectMapper.constructor_arg('reference_images')
    def carg_reference_images(self, builder):
        return 'None'

    @ObjectMapper.constructor_arg('name')
    def carg_name(self, builder):
        return builder.name

    # @ObjectMapper.constructor_arg('source')
    # def source_gettr(self, builder):

    #     if 'source' in builder.attributes:
    #         return builder.attributes['source']
    #     else:
    #         return 'None2'


    # def __get_override_carg(self, *args, **kwargs):
    #     return self.hack_get_override_carg(*args, **kwargs)

    # @ObjectMapper.constructor_arg('imaging_plane')
    # def carg_imaging_plane(self, builder):
    #     return 'imaging_plane_1' #builder.get('imaging_plane')

    # @ObjectMapper.constructor_arg('reference_images')
    # def carg_reference_images(self, builder):
    #     return builder.get('image_series') # builder.get('reference_images')
