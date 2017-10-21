from .. import ObjectMapper
from pynwb.legacy import register_map
from pynwb.ophys import PlaneSegmentation, ImageSegmentation

@register_map(PlaneSegmentation)
class PlaneSegmentationMap(ObjectMapper):

    def __init__(self, spec):
        super(PlaneSegmentationMap, self).__init__(spec)
        roi_spec = self.spec.get_neurodata_type('ROI')
        self.map_const_arg('roi_list', roi_spec)

    @ObjectMapper.constructor_arg('roi_list')
    def carg_roi_list(self, builder):
        return builder.get('rois')

    @ObjectMapper.constructor_arg('imaging_plane')
    def carg_imaging_plane(self, *args):
        builder = args[0]
        if len(args) < 2:
            return builder.name # I think this is the hack you had in there before
        manager = args[1]
        root = builder
        parent = root.parent
        while parent is not None:
            root = parent
            parent = root.parent
        ip_name = builder['imaging_plane_name']
        ip_builder = root['general/optophysiology/%s' % ip_name]
        imaging_plane = manager.construct(ip_builder)
        return imaging_plane

    @ObjectMapper.constructor_arg('reference_images')
    def carg_reference_images(self, builder):
        return builder.get('image_series') # builder.get('reference_images')


@register_map(PlaneSegmentation)
class ROIMap(ObjectMapper):

    @ObjectMapper.constructor_arg('reference_images')
    def carg_reference_images(self, builder):
        return 'None'

    @ObjectMapper.constructor_arg('name')
    def carg_name(self, builder):
        return builder.get('name')

    # @ObjectMapper.constructor_arg('imaging_plane')
    # def carg_imaging_plane(self, builder):
    #     return 'imaging_plane_1' #builder.get('imaging_plane')

    # @ObjectMapper.constructor_arg('reference_images')
    # def carg_reference_images(self, builder):
    #     return builder.get('image_series') # builder.get('reference_images')
