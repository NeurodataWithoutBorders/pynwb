import numpy as np

from pynwb.ophys import PlaneSegmentation, TwoPhotonSeries

from .. import ObjectMapper, register_map


@register_map(PlaneSegmentation)
class PlaneSegmentationMap(ObjectMapper):

    # This might be needed for 2.0 as well
    def __init__(self, spec):
        super(PlaneSegmentationMap, self).__init__(spec)

        reference_images_spec = self.spec.get_group('reference_images').get_neurodata_type('ImageSeries')
        self.map_spec('reference_images', reference_images_spec)

    @ObjectMapper.constructor_arg('imaging_plane')
    def carg_imaging_plane(self, *args):
        builder = args[0]
        if len(args) < 2:
            return builder.name  # I think this is the hack you had in there before
        manager = args[1]
        root = builder
        parent = root.parent
        while parent is not None:
            root = parent
            parent = root.parent
        ip_name = builder['imaging_plane_name']['data']
        ip_builder = root['general/optophysiology/%s' % ip_name]
        imaging_plane = manager.construct(ip_builder)
        return imaging_plane


@register_map(TwoPhotonSeries)
class TwoPhotonSeriesMap(ObjectMapper):

    @ObjectMapper.constructor_arg('data')
    def carg_data(self, *args):
        builder = args[0]
        if builder.name in ('2p_image_series',):
            return np.array([-1.])

    @ObjectMapper.constructor_arg('unit')
    def carg_unit(self, *args):
        builder = args[0]
        if builder.name in ('2p_image_series',):
            return 'None'

    @ObjectMapper.constructor_arg('imaging_plane')
    def carg_imaging_plane(self, *args):
        builder = args[0]
        if len(args) < 2:
            return builder.name  # I think this is the hack you had in there before
        manager = args[1]
        root = builder
        parent = root.parent
        while parent is not None:
            root = parent
            parent = root.parent
        ip_name = builder['imaging_plane']['data']
        ip_builder = root['general/optophysiology/%s' % ip_name]
        imaging_plane = manager.construct(ip_builder)
        return imaging_plane
