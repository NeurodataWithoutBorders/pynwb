from .. import ObjectMapper
from pynwb.legacy import register_map
from pynwb.ogen import OptogeneticSeries

@register_map(OptogeneticSeries)
class OptogeneticSeriesMap(ObjectMapper):

    @ObjectMapper.constructor_arg('site')
    def carg_site(self, *args):
        builder = args[0]
        manager = args[1]
        root = builder
        parent = root.parent
        while parent is not None:
            root = parent
            parent = root.parent
        site_name = builder['site']['data']
        site_builder = root['general/optogenetics/%s' % site_name]
        site = manager.construct(site_builder)
        return site
