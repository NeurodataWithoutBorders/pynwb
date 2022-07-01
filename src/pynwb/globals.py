"""Definitions of global values used across the project."""
import hdmf
from hdmf.spec import NamespaceCatalog
from hdmf.build import TypeMap

from .spec import NWBDatasetSpec, NWBGroupSpec, NWBNamespace  # noqa E402

CORE_NAMESPACE = 'core'
__core_ns_file_name = 'nwb.namespace.yaml'

# a global namespace catalog
global __NS_CATALOG
global __TYPE_MAP

__NS_CATALOG = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)

hdmf_typemap = hdmf.common.get_type_map()
__TYPE_MAP = TypeMap(__NS_CATALOG)
__TYPE_MAP.merge(hdmf_typemap, ns_catalog=True)
