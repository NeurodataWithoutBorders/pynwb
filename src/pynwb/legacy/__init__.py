from .map import ObjectMapperLegacy as ObjectMapper
from .map import TypeMapLegacy as TypeMap
from ..spec import NWBDatasetSpec, NWBGroupSpec, NWBNamespace
from form.spec import NamespaceCatalog

__NS_CATALOG = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)
__TYPE_MAP = TypeMap(__NS_CATALOG)

def get_type_map(**kwargs):
    '''
    Get a TypeMap to use for I/O for Allen Institute Brain Observatory files (NWB v1.0.6)
    '''
    return __TYPE_MAP
