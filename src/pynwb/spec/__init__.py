from .spec import NAME_WILDCARD

from .spec import Spec
from .spec import AttributeSpec
from .spec import DatasetSpec
from .spec import LinkSpec
from .spec import GroupSpec
from .namespace import SpecNamespace
from .namespace import NamespaceCatalog

from ..utils import docval

CORE_NAMESPACE = 'core'
__core_ns_file_name = 'nwb.namespace.yaml'

def __get_resources():
    from pkg_resources import resource_filename
    from os.path import join
    ret = dict()
    ret['namespace_path'] = join(resource_filename(__name__, 'data'), __core_ns_file_name)
    return ret

def __get_namespace_catalog(namespace_path, catalog):
    namespaces = SpecNamespace.build_namespaces(namespace_path, catalog)
    for ns_name, ns in namespaces.items():
        catalog.add_namespace(ns_name, ns)
    return catalog

__resources = __get_resources()

NAMESPACES = __get_namespace_catalog(__resources['namespace_path'], NamespaceCatalog())

@docval({'name': 'name', 'type': str, 'doc': 'the name of this namespace'},
        {'name': 'namespace', 'type': SpecNamespace, 'doc': 'the SpecNamespace object'},
        is_method=False)
def add_namespace(**kwargs):
    name, namespace = getargs('name', 'namespace', kwargs)
    NAMESPACES[name] = namespace

@docval({'name': 'namespace_path', 'type': str, 'doc': 'the path to the YAML with the namespace definition'},
        is_method=False)
def load_namespace(**kwargs):
    namespace_path = getargs('namespace_path', kwargs)
    __get_namespace_catalog(namespace_path, NAMESPACES)
