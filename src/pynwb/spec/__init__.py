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

def __build_namespaces(data_dir_path):
    from glob import iglob
    import ruamel.yaml as yaml
    from itertools import chain
    from os.path import join
    from .catalog import SpecCatalog
    spec_catalog = SpecCatalog()
    exts = ['yaml', 'json']
    glob_str = join(data_dir_path, "*.%s")
    specs = dict()
    namespaces = list()
    # load all specs before resolving namespaces
    for path in chain(*[iglob(glob_str % ext) for ext in exts]):
        with open(path, 'r') as stream:
            d  = yaml.safe_load(stream)
            for k, v in d.items():
                if k == 'specs':
                    for spec_dict in v:
                        spec_obj = GroupSpec.build_spec(spec_dict)
                        if path not in specs:
                            specs[path] = dict()
                        specs[path][spec_obj.neurodata_type_def] = spec_obj

                elif k == 'namespaces':
                    namespaces.extend(v)
    # build namespaces with SpecCatalogs
    ret = dict()
    for ns in namespaces:
        catalog = SpecCatalog()
        if 'schema' in ns:
            for s in ns['schema']:
                if 'source' not in s:
                    continue
                for spec in specs[s['source']]:
                    ndts = spec.values()
                    if 'neurodata_types' in s:
                        ndts = filter(lambda x: x in set(s['neurodata_types']), ndts)
                    for ndt_spec in ndts:
                        catalog.auto_register(ndt_spec, s['source'])

        ret[ns['name']] = SpecNamespace.build_namespace(**ns, catalog=catalog)


    return ret

__resources = __get_resources()

NAMESPACES = __build_namespaces(__resources['data_dir_path'])
DEFAULT_NAMESPACE = 'core'
