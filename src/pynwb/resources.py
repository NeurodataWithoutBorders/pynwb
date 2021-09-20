from hdmf.common import ExternalResources
from . import EXP_NAMESPACE, register_class, get_type_map

@register_class('NWBExternalResources', EXP_NAMESPACE)
class NWBExternalResources(ExternalResources):

    @docval({@docval(*get_docval(ExternalResources.__init__))})
    def __init__(self, **kwargs):
        super().__init__(name, keys, resources, entities, objects, object_keys)
        self.type_map = kwargs['type_map'] or get_type_map()
