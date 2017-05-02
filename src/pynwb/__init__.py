'''This ackage will contain functions, classes, and objects
for reading and writing data in NWB format
'''
import os.path


from form.spec import NamespaceCatalog, SpecNamespace
from form.utils import docval, getargs

from .core import NWBContainer

CORE_NAMESPACE = 'core'
__core_ns_file_name = 'nwb.namespace.yaml'

def __get_resources():
    from pkg_resources import resource_filename
    from os.path import join
    ret = dict()
    ret['namespace_path'] = join(resource_filename(__name__, 'data'), __core_ns_file_name)
    return ret

def __get_namespace_catalog(namespace_path, catalog):
    if os.path.exists(namespace_path):
        namespaces = SpecNamespace.build_namespaces(namespace_path, catalog)
        for ns_name, ns in namespaces.items():
            catalog.add_namespace(ns_name, ns)
    return catalog

__resources = __get_resources()

__NAMESPACES = __get_namespace_catalog(__resources['namespace_path'], NamespaceCatalog(CORE_NAMESPACE))

@docval({'name': 'name', 'type': str, 'doc': 'the name of this namespace'},
        {'name': 'namespace', 'type': SpecNamespace, 'doc': 'the SpecNamespace object'},
        is_method=False)
def register_namespace(**kwargs):
    name, namespace = getargs('name', 'namespace', kwargs)
    __NAMESPACES[name] = namespace

@docval({'name': 'namespace_path', 'type': str, 'doc': 'the path to the YAML with the namespace definition'},
        is_method=False)
def load_namespace(**kwargs):
    namespace_path = getargs('namespace_path', kwargs)
    __get_namespace_catalog(namespace_path, __NAMESPACES)

def get_type_map():
    from form.build import TypeMap, ObjectMapper
    ret = TypeMap(__NAMESPACES)
    ret.register_map(NWBContainer, ObjectMapper)
    return ret

__TYPE_MAP = get_type_map()

# added here for convenience to users
def BuildManager(type_map=__TYPE_MAP):
    from form.build import BuildManager
    return BuildManager(type_map)

@docval({'name': 'neurodata_type', 'type': str, 'doc': 'the neurodata_type to get the spec for'},
        {'name': 'namespace', 'type': str, 'doc': 'the name of the namespace'},
        {"name": "container_cls", "type": type, "doc": "the class to map to the specified neurodata_type", 'default': None},
        is_method=False)
def register_class(**kwargs):
    neurodata_type, namespace, container_cls = getargs('neurodata_type', 'namespace', 'container_cls', kwargs)
    def _dec(cls):
        __TYPE_MAP.register_container_type(namespace, neurodata_type, cls)
        return cls
    if container_cls is None:
        return _dec
    else:
        _dec(container_cls)

@docval({"name": "container_cls", "type": type, "doc": "the Container class for which the given ObjectMapper class gets used for"},
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

from . import io as __io
from .base import TimeSeries, Module, Interface
from .file import NWBFile

