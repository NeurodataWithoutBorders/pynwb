from pynwb.ogen import OptogeneticSeries

from .. import ObjectMapper, register_map


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
