from .spec import NAME_WILDCARD

from .spec import Spec
from .spec import AttributeSpec
from .spec import DatasetSpec
from .spec import LinkSpec
from .spec import GroupSpec

def __get_resources():
    from pkg_resources import resource_filename
    import os
    ret = dict()
    ret['data_dir_path'] = resource_filename(__name__, '../data')
    type_name_map_path = resource_filename(__name__, '../type_name_map.yaml')
    ret['type_name_map'] = dict()
    if os.path.exists(type_name_map_path):
        with open(type_name_map_path, 'r') as stream:
            ret['type_name_map'] = yaml.safe_load(stream)
    return ret

def __build_catalog(data_dir_path):
    from glob import iglob
    import ruamel.yaml as yaml
    from itertools import chain
    from os.path import join
    from .spec import SpecCatalog
    spec_catalog = SpecCatalog()
    exts = ['yaml', 'json']
    glob_str = join(data_dir_path, "*.%s")
    for path in chain(*[iglob(glob_str % ext) for ext in exts]):
        with open(path, 'r') as stream:
            for obj in yaml.safe_load(stream):
                spec_obj = GroupSpec.build_spec(obj)
                spec_catalog.auto_register(spec_obj)
    return spec_catalog

__resources = __get_resources()

CATALOG = __build_catalog(__resources['data_dir_path'])
