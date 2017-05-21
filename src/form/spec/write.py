import copy
import json
import ruamel.yaml as yaml
import os.path

from .namespace import SpecNamespace
from .spec import GroupSpec, DatasetSpec

from ..utils import docval, getargs, popargs


class NamespaceBuilder(object):

    @docval({'name': 'doc', 'type': str, 'doc': 'a description about what this namespace represents'},
            {'name': 'name', 'type': str, 'doc': 'the name of this namespace'},
            {'name': 'full_name', 'type': str, 'doc': 'extended full name of this namespace', 'default': None},
            {'name': 'version', 'type': (str, tuple, list), 'doc': 'Version number of the namespace', 'default': None},
            {'name': 'author', 'type': (str, list), 'doc': 'Author or list of authors.', 'default': None},
            {'name': 'contact', 'type': (str, list), 'doc': 'List of emails. Ordering should be the same as for author', 'default': None},
            {'name': 'namespace_cls', 'type': type, 'doc': 'the SpecNamespace type', 'default': SpecNamespace})
    def __init__(self, **kwargs):
        ns_cls = popargs('namespace_cls', kwargs)
        self.__ns_args = copy.deepcopy(kwargs)
        self.__namespaces = dict()
        self.__sources = dict()
        self.__dt_key = ns_cls.types_key()

    @docval({'name': 'path', 'type': str, 'doc': 'the path to write the spec to'},
            {'name': 'spec', 'type': (GroupSpec, DatasetSpec), 'doc': 'the Spec to add'})
    def add_spec(self, **kwargs):
        path, spec = getargs('path', 'spec', kwargs)
        self.add_source(path)
        self.__sources[path].setdefault(self.__dt_key, list()).append(spec)

    @docval({'name': 'path', 'type': str, 'doc': 'the path to write the spec to'})
    def add_source(self, **kwargs):
        path = getargs('path', kwargs)
        self.__sources.setdefault(path, {'source': path})

    @docval({'name': 'data_type', 'type': str, 'doc': 'the data type to include'},
            {'name': 'source', 'type': str, 'doc': 'the source file to include the type from', 'default': None},
            {'name': 'namespace', 'type': str, 'doc': 'the namespace from which to include the data type', 'default': None})
    def include_type(self, **kwargs):
        dt, src, ns = getargs('data_type', 'source', 'namespace', kwargs)
        if src is not None:
            self.add_source(source)
            self.__sources[path].setdefault(self.__dt_key, list()).append(dt)
        elif ns is not None:
            self.include_namespace(ns)
            self.__namespaces[ns].setdefault(self.__dt_key, list()).append(dt)
        else:
            raise ValueError("must specify 'source' or 'namespace' when including type")

    @docval({'name': 'namespace', 'type': str, 'doc': 'the namespace to include'})
    def include_namespace(self, **kwargs):
        namespace = getargs('namespace', kwargs)
        self.__namespaces.setdefault(namespace, {'namespace': namespace})

    def __dump_spec(self, specs, stream):
        yaml.dump(json.loads(json.dumps(specs)), stream, default_flow_style=False)

    @docval({'name': 'path', 'type': str, 'doc': 'the path to write the spec to'})
    def export(self, **kwargs):
        ns_path = getargs('path', kwargs)
        outdir = os.path.dirname(ns_path)
        ns_args = copy.copy(self.__ns_args)
        ns_args['schema'] = list()
        for ns, info in self.__namespaces.items():
            ns_args['schema'].append(info)
        for path, info  in self.__sources.items():
            out = dict()
            dts = list()
            for spec in info[self.__dt_key]:
                if isinstance(spec, GroupSpec):
                    out.setdefault('groups', list()).append(spec)
                elif isinstance(spec, DatasetSpec):
                    out.setdefault('datasets', list()).append(spec)
                else:
                    dts.append(spec)
            item = {'source': path}
            if out and dts:
                raise ValueError('cannot include from source if writing to source')
            elif dts:
                print('including types from %s' % path)
                item[self.__dt_key] = dts
            elif out:
                print('writing all specs to %s' % path)
                with open(os.path.join(outdir, path), 'w') as stream:
                    self.__dump_spec(out, stream)
            ns_args['schema'].append(item)
        with open(ns_path, 'w') as stream:
            self.__dump_spec({'namespaces': [SpecNamespace.build_namespace(**ns_args)]}, stream)
