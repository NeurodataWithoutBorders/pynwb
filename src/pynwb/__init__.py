'''This ackage will contain functions, classes, and objects
for reading and writing data in NWB format
'''
import os.path
from copy import deepcopy
from warnings import warn

CORE_NAMESPACE = 'core'

from .form.spec import NamespaceCatalog  # noqa: E402
from .form.utils import docval, getargs, popargs, call_docval_func  # noqa: E402
from .form.backends.io import FORMIO  # noqa: E402
from .form.backends.hdf5 import HDF5IO  # noqa: E402
from .form.validate import ValidatorMap  # noqa: E402
from .form.build import BuildManager  # noqa: E402

from .spec import NWBDatasetSpec, NWBGroupSpec, NWBNamespace  # noqa: E402

__core_ns_file_name = 'nwb.namespace.yaml'


def __get_resources():
    from pkg_resources import resource_filename
    from os.path import join
    ret = dict()
    ret['namespace_path'] = join(resource_filename(__name__, 'data'), __core_ns_file_name)
    return ret


def _get_resources():
    # LEGACY: Needed to support legacy implementation.
    return __get_resources()


# a global namespace catalog
global __NS_CATALOG
global __TYPE_MAP

__NS_CATALOG = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)

from .form.build import TypeMap as TypeMap  # noqa: E402

__TYPE_MAP = TypeMap(__NS_CATALOG)


@docval({'name': 'extensions', 'type': (str, TypeMap, list),
         'doc': 'a path to a namespace, a TypeMap, or a list consisting paths to namespaces and TypeMaps',
         'default': None},
        returns="the namespaces loaded from the given file", rtype=tuple,
        is_method=False)
def get_type_map(**kwargs):
    '''
    Get a BuildManager to use for I/O using the given extensions. If no extensions are provided,
    return a BuildManager that uses the core namespace
    '''
    extensions = getargs('extensions', kwargs)
    type_map = None
    if extensions is None:
        type_map = deepcopy(__TYPE_MAP)
    else:
        if isinstance(extensions, TypeMap):
            type_map = extensions
        else:
            type_map = deepcopy(__TYPE_MAP)
        if isinstance(extensions, list):
            for ext in extensions:
                if isinstance(ext, str):
                    type_map.load_namespaces(ext)
                elif isinstance(ext, TypeMap):
                    type_map.merge(ext)
                else:
                    msg = 'extensions must be a list of paths to namespace specs or a TypeMaps'
                    raise ValueError(msg)
        elif isinstance(extensions, str):
            type_map.load_namespaces(extensions)
        elif isinstance(extensions, TypeMap):
            type_map.merge(extensions)
    return type_map


@docval({'name': 'extensions', 'type': (str, TypeMap, list),
         'doc': 'a path to a namespace, a TypeMap, or a list consisting paths to namespaces and TypeMaps',
         'default': None},
        returns="the namespaces loaded from the given file", rtype=tuple,
        is_method=False)
def get_manager(**kwargs):
    '''
    Get a BuildManager to use for I/O using the given extensions. If no extensions are provided,
    return a BuildManager that uses the core namespace
    '''
    type_map = call_docval_func(get_type_map, kwargs)
    return BuildManager(type_map)


@docval({'name': 'namespace_path', 'type': str,
         'doc': 'the path to the YAML with the namespace definition'},
        returns="the namespaces loaded from the given file", rtype=tuple,
        is_method=False)
def load_namespaces(**kwargs):
    '''
    Load namespaces from file
    '''
    namespace_path = getargs('namespace_path', kwargs)
    return __TYPE_MAP.load_namespaces(namespace_path)


# load the core namespace i.e. base NWB specification
__resources = __get_resources()
if os.path.exists(__resources['namespace_path']):
    load_namespaces(__resources['namespace_path'])


@docval(returns="a tuple of the available namespaces", rtype=tuple)
def available_namespaces(**kwargs):
    return tuple(__NS_CATALOG.namespaces.keys())


# a function to register a container classes with the global map
@docval({'name': 'neurodata_type', 'type': str, 'doc': 'the neurodata_type to get the spec for'},
        {'name': 'namespace', 'type': str, 'doc': 'the name of the namespace'},
        {"name": "container_cls", "type": type,
         "doc": "the class to map to the specified neurodata_type", 'default': None},
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


# a function to get the container class for a give type
@docval({'name': 'neurodata_type', 'type': str,
         'doc': 'the neurodata_type to get the NWBConatiner class for'},
        {'name': 'namespace', 'type': str, 'doc': 'the namespace the neurodata_type is defined in'},
        is_method=False)
def get_class(**kwargs):
    """Get the class object of the NWBContainer subclass corresponding to a given neurdata_type.
    """
    neurodata_type, namespace = getargs('neurodata_type', 'namespace', kwargs)
    return __TYPE_MAP.get_container_cls(namespace, neurodata_type)


@docval({'name': 'io', 'type': FORMIO,
         'doc': 'the FORMIO object to read from'},
        {'name': 'namespace', 'type': str,
         'doc': 'the namespace to validate against', 'default': CORE_NAMESPACE},
        returns="errors in the file", rtype=list,
        is_method=False)
def validate(**kwargs):
    """Validate an NWB file against a namespace"""
    io, namespace = getargs('io', 'namespace', kwargs)
    builder = io.read_builder()
    validator = ValidatorMap(__NS_CATALOG.get_namespace(namespace))
    return validator.validate(builder)


class NWBHDF5IO(HDF5IO):

    @docval({'name': 'path', 'type': str, 'doc': 'the path to the HDF5 file to write to'},
            {'name': 'mode', 'type': str,
             'doc': 'the mode to open the HDF5 file with, one of ("w", "r", "r+", "a", "w-")', 'default': 'a'},
            {'name': 'load_namespaces', 'type': bool,
             'doc': 'whether or not to load cached namespaces from given path', 'default': False},
            {'name': 'manager', 'type': BuildManager, 'doc': 'the BuildManager to use for I/O', 'default': None},
            {'name': 'extensions', 'type': (str, TypeMap, list),
             'doc': 'a path to a namespace, a TypeMap, or a list consisting paths \
             to namespaces and TypeMaps', 'default': None})
    def __init__(self, **kwargs):
        path, mode, manager, extensions, load_namespaces =\
            popargs('path', 'mode', 'manager', 'extensions', 'load_namespaces', kwargs)
        if load_namespaces:
            if manager is not None:
                warn("loading namespaces from file - ignoring 'manager'")
            if extensions is not None:
                warn("loading namespaces from file - ignoring 'extensions' argument")
            if 'w' in mode:
                raise ValueError("cannot load namespaces from file when writing to it")

            # XXX: Leaving this here in case we want to revert to this strategy for
            #      loading cached namespaces
            # ns_catalog = NamespaceCatalog(NWBGroupSpec, NWBDatasetSpec, NWBNamespace)
            # super(NWBHDF5IO, self).load_namespaces(ns_catalog, path)
            # tm = TypeMap(ns_catalog)
            # tm.copy_mappers(get_type_map())

            tm = get_type_map()
            super(NWBHDF5IO, self).load_namespaces(tm, path)
            manager = BuildManager(tm)
        else:
            if manager is not None and extensions is not None:
                raise ValueError("'manager' and 'extensions' cannot be specified together")
            elif extensions is not None:
                manager = get_manager(extensions=extensions)
            elif manager is None:
                manager = get_manager()
        super(NWBHDF5IO, self).__init__(path, manager, mode=mode)


from . import io as __io  # noqa: F401,E402
from .core import NWBContainer, NWBData  # noqa: F401,E402
from .base import TimeSeries, ProcessingModule  # noqa: F401,E402
from .file import NWBFile  # noqa: E402, F401

from . import behavior  # noqa: F401,E402
from . import ecephys  # noqa: F401,E402
from . import epoch  # noqa: F401,E402
from . import icephys  # noqa: F401,E402
from . import image  # noqa: F401,E402
from . import misc  # noqa: F401,E402
from . import ogen  # noqa: F401,E402
from . import ophys  # noqa: F401,E402
from . import retinotopy  # noqa: F401,E402
from . import legacy  # noqa: F401,E402

from ._version import get_versions  # noqa: E402
__version__ = get_versions()['version']
del get_versions
