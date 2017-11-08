
from ..form.spec import NamespaceCatalog
from ..form.utils import docval, getargs
from ..spec import NWBDatasetSpec, NWBGroupSpec, NWBNamespace
from .. import _get_resources, get_type_map, NWBContainer

from .map import ObjectMapperLegacy as ObjectMapper
from .map import TypeMapLegacy as TypeMap


__NS_CATALOG = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)
__TYPE_MAP = TypeMap(__NS_CATALOG)

# load the core namespace i.e. base NWB specification
__resources = _get_resources()
__TYPE_MAP.load_namespaces(__resources['namespace_path'])
__TYPE_MAP.merge(get_type_map())

# Register new ObjectMapper with the new TypeMap:
__TYPE_MAP.register_map(NWBContainer, ObjectMapper)


def get_type_map(**kwargs):
    """
    Get a TypeMap to use for I/O for Allen Institute Brain Observatory files (NWB v1.0.6)
    """
    return __TYPE_MAP


# a function to register an object mapper for a container class
@docval({"name": "container_cls", "type": type,
         "doc": "the Container class for which the given ObjectMapper class gets used for"},
        {"name": "mapper_cls", "type": type, "doc": "the ObjectMapper class to use to map", 'default': None},
        is_method=False)
def register_map(**kwargs):
    """Register an ObjectMapper to use for a Container class type
    If mapper_cls is not specified, returns a decorator for registering an ObjectMapper class
    as the mapper for container_cls. If mapper_cls specified, register the class as the mapper for container_cls
    """

    container_cls, mapper_cls = getargs('container_cls', 'mapper_cls', kwargs)

    def _dec(cls):
        __TYPE_MAP.register_map(container_cls, cls)
        return cls
    if mapper_cls is None:
        return _dec
    else:
        _dec(mapper_cls)


from . import io  # noqa: F401
