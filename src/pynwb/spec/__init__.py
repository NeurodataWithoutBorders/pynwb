from .spec import NAME_WILDCARD

from .spec import Spec
from .spec import AttributeSpec
from .spec import DatasetSpec
from .spec import LinkSpec
from .spec import GroupSpec
from .namespace import SpecNamespace

def __get_resources():
    from pkg_resources import resource_filename
    import os
    ret = dict()
    ret['data_dir_path'] = resource_filename(__name__, 'data')
    return ret

def __get_namespace_catalog(data_dir_path, catalog):
    namespaces = SpecNameSpace.build_namespace(data_dir_path)
    for ns_name, ns in namespaces.items():
        catalog.add_namespace(ns_name, ns)

__resources = __get_resources()

DEFAULT_NAMESPACE = 'core'
NAMESPACES = __get_namespace_catalog(__resources['data_dir_path'], NamespaceCatalog())

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
