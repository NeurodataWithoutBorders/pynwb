from .. import ObjectMapper
from pynwb.legacy import register_map
from pynwb.misc import AbstractFeatureSeries

@register_map(AbstractFeatureSeries)
class AbstractFeatureSeriesMap(ObjectMapper):

    @ObjectMapper.constructor_arg('feature_units')
    def carg_feature_units(self, *args):
        return ['None', 'None', 'None']