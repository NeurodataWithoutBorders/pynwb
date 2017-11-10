from pynwb.misc import AbstractFeatureSeries

from .. import ObjectMapper, register_map


@register_map(AbstractFeatureSeries)
class AbstractFeatureSeriesMap(ObjectMapper):

    @ObjectMapper.constructor_arg('feature_units')
    def carg_feature_units(self, *args):
        return ['None', 'None', 'None']
