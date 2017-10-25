'''This ackage will contain functions, classes, and objects
for reading and writing data in NWB format
'''
import os.path

CORE_NAMESPACE = 'core'

from .form.spec import NamespaceCatalog
from .form.utils import docval, getargs
from .form.backends.io import FORMIO
from .form.validate import ValidatorMap

from .spec import NWBAttributeSpec, NWBLinkSpec, NWBDatasetSpec, NWBGroupSpec, NWBNamespace, NWBNamespaceBuilder


__core_ns_file_name = 'nwb.namespace.yaml'
def __get_resources():
    from pkg_resources import resource_filename
    from os.path import join
    ret = dict()
    ret['namespace_path'] = join(resource_filename(__name__, 'data'), __core_ns_file_name)
    return ret

# a global namespace catalog
global __NS_CATALOG
global __TYPE_MAP

__NS_CATALOG = NamespaceCatalog(CORE_NAMESPACE, NWBGroupSpec, NWBDatasetSpec, NWBNamespace)

from .form.build import TypeMap as __TypeMap
from .form.build import ObjectMapper as __ObjectMapper
def get_type_map():
    ret = __TypeMap(__NS_CATALOG)
    return ret

# a global type map
__TYPE_MAP = get_type_map()

def get_global_type_map():
    #ret = __TypeMap(__NS_CATALOG)
    ret = __TYPE_MAP
    return ret

@docval({'name': 'namespace_path', 'type': str, 'doc': 'the path to the YAML with the namespace definition'},
        returns="the namespaces loaded from the given file", rtype=tuple,
        is_method=False)
def load_namespaces(**kwargs):
    '''Load namespaces from file'''
    namespace_path = getargs('namespace_path', kwargs)
    return __TYPE_MAP.load_namespaces(namespace_path)

# load the core namespace i.e. base NWB specification
__resources = __get_resources()
if os.path.exists(__resources['namespace_path']):
    load_namespaces(__resources['namespace_path'])

# added here for convenience to users
from .form.build import BuildManager as __BuildManager
@docval({'name': 'type_map', 'type': __TypeMap, 'doc': 'the path to the YAML with the namespace definition', 'default': None},
        is_method=False)
def get_build_manager(**kwargs):
    type_map = getargs('type_map', kwargs)
    if type_map is None:
        type_map = __TYPE_MAP
    return __BuildManager(type_map)

@docval(returns="a tuple of the available namespaces", rtype=tuple)
def available_namespaces(**kwargs):
    return tuple(__NS_CATALOG.namespaces.keys())

# a function to register a container classes with the global map
@docval({'name': 'neurodata_type', 'type': str, 'doc': 'the neurodata_type to get the spec for'},
        {'name': 'namespace', 'type': str, 'doc': 'the name of the namespace'},
        {"name": "container_cls", "type": type, "doc": "the class to map to the specified neurodata_type", 'default': None},
        is_method=False)
def register_class(**kwargs):
    """Register an NWBContainer class to use for reading and writing a neurodata_type from a specification
    If container_cls is not specified, returns a decorator for registering an NWBContainer subclass
    as the class for neurodata_type in namespace.
    """
    neurodata_type, namespace, container_cls = getargs('neurodata_type', 'namespace', 'container_cls', kwargs)
    def _dec(cls):
        __TYPE_MAP.register_container_type(namespace, neurodata_type, cls)
        return cls
    if container_cls is None:
        return _dec
    else:
        _dec(container_cls)

# a function to register an object mapper for a container class
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

# a function to get the container class for a give type
@docval({'name': 'neurodata_type', 'type': str, 'doc': 'the neurodata_type to get the NWBConatiner class for'},
        {'name': 'namespace', 'type': str, 'doc': 'the namespace the neurodata_type is defined in'},
        is_method=False)
def get_class(**kwargs):
    """Get the class object of the NWBContainer subclass corresponding to a given neurdata_type.
    """
    neurodata_type, namespace = getargs('neurodata_type', 'namespace', kwargs)
    return __TYPE_MAP.get_container_cls(namespace, neurodata_type)

@docval({'name': 'io', 'type': FORMIO, 'doc': 'the FORMIO object to read from'},
        {'name': 'namespace', 'type': str, 'doc': 'the namespace to validate against', 'default':CORE_NAMESPACE},
        returns="errors in the file", rtype=list,
        is_method=False)
def validate(**kwargs):
    """Validate an NWB file against a namespace"""
    io, namespace = getargs('io', 'namespace', kwargs)
    builder = io.read_builder()
    validator = ValidatorMap(__NS_CATALOG.get_namespace(namespace))
    return validator.validate(builder)


from . import io as __io
from .core import NWBContainer, NWBData
from .base import TimeSeries, ProcessingModule
from .file import NWBFile

NWBFile.set_version(__NS_CATALOG.get_namespace(CORE_NAMESPACE).version)

from . import behavior
from . import ecephys
from . import epoch
from . import icephys
from . import image
from . import misc
from . import ogen
from . import ophys
from . import retinotopy

__TypeMap.register_default(__TYPE_MAP)
