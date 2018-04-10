import copy
import json
import ruamel.yaml as yaml
import os.path
from collections import OrderedDict
from six import with_metaclass
from abc import ABCMeta, abstractmethod

from .namespace import SpecNamespace
from .spec import GroupSpec, DatasetSpec
from .catalog import SpecCatalog

from ..utils import docval, getargs, popargs


class SpecWriter(with_metaclass(ABCMeta, object)):

    @abstractmethod
    def write_spec(self, spec_file_dict, path):
        pass

    @abstractmethod
    def write_namespace(self, namespace, path):
        pass


class YAMLSpecWriter(SpecWriter):

    @docval({'name': 'outdir',
             'type': str,
             'doc': 'the path to write the directory to output the namespace and specs too', 'default': '.'})
    def __init__(self, **kwargs):
        self.__outdir = getargs('outdir', kwargs)

    def __dump_spec(self, specs, stream):
        yaml.safe_dump(json.loads(json.dumps(specs)), stream, default_flow_style=False)

    def write_spec(self, spec_file_dict, path):
        with open(os.path.join(self.__outdir, path), 'w') as stream:
            self.__dump_spec(spec_file_dict, stream)

    def write_namespace(self, namespace, path):
        with open(os.path.join(self.__outdir, path), 'w') as stream:
            self.__dump_spec({'namespaces': [namespace]}, stream)


class NamespaceBuilder(object):
    ''' A class for building namespace and spec files '''

    @docval({'name': 'doc', 'type': str, 'doc': 'a description about what name namespace represents'},
            {'name': 'name', 'type': str, 'doc': 'the name of namespace'},
            {'name': 'full_name', 'type': str, 'doc': 'extended full name of name namespace', 'default': None},
            {'name': 'version', 'type': (str, tuple, list), 'doc': 'Version number of the namespace', 'default': None},
            {'name': 'author', 'type': (str, list), 'doc': 'Author or list of authors.', 'default': None},
            {'name': 'contact', 'type': (str, list),
             'doc': 'List of emails. Ordering should be the same as for author', 'default': None},
            {'name': 'namespace_cls', 'type': type, 'doc': 'the SpecNamespace type', 'default': SpecNamespace})
    def __init__(self, **kwargs):
        ns_cls = popargs('namespace_cls', kwargs)
        self.__ns_args = copy.deepcopy(kwargs)
        self.__namespaces = OrderedDict()
        self.__sources = OrderedDict()
        self.__catalog = SpecCatalog()
        self.__dt_key = ns_cls.types_key()

    @docval({'name': 'source', 'type': str, 'doc': 'the path to write the spec to'},
            {'name': 'spec', 'type': (GroupSpec, DatasetSpec), 'doc': 'the Spec to add'})
    def add_spec(self, **kwargs):
        ''' Add a Spec to the namespace '''
        source, spec = getargs('source', 'spec', kwargs)
        self.__catalog.auto_register(spec, source)
        self.add_source(source)
        self.__sources[source].setdefault(self.__dt_key, list()).append(spec)

    @docval({'name': 'source', 'type': str, 'doc': 'the path to write the spec to'})
    def add_source(self, **kwargs):
        ''' Add a source file to the namespace '''
        source = getargs('source', kwargs)
        if '/' in source or source[0] == '.':
            raise ValueError('source must be a base file')
        self.__sources.setdefault(source, {'source': source})

    @docval({'name': 'data_type', 'type': str, 'doc': 'the data type to include'},
            {'name': 'source', 'type': str, 'doc': 'the source file to include the type from', 'default': None},
            {'name': 'namespace', 'type': str,
             'doc': 'the namespace from which to include the data type', 'default': None})
    def include_type(self, **kwargs):
        ''' Include a data type from an existing namespace or source '''
        dt, src, ns = getargs('data_type', 'source', 'namespace', kwargs)
        if src is not None:
            self.add_source(source)  # noqa: F821
            self.__sources[path].setdefault(self.__dt_key, list()).append(dt)  # noqa: F821
        elif ns is not None:
            self.include_namespace(ns)
            self.__namespaces[ns].setdefault(self.__dt_key, list()).append(dt)
        else:
            raise ValueError("must specify 'source' or 'namespace' when including type")

    @docval({'name': 'namespace', 'type': str, 'doc': 'the namespace to include'})
    def include_namespace(self, **kwargs):
        ''' Include an entire namespace '''
        namespace = getargs('namespace', kwargs)
        self.__namespaces.setdefault(namespace, {'namespace': namespace})

    @docval({'name': 'path', 'type': str, 'doc': 'the path to write the spec to'},
            {'name': 'outdir',
             'type': str,
             'doc': 'the path to write the directory to output the namespace and specs too', 'default': '.'},
            {'name': 'writer',
             'type': SpecWriter,
             'doc': 'the SpecWriter to use to write the namespace', 'default': None})
    def export(self, **kwargs):
        ''' Export the namespace to the given path.

        All new specification source files will be written in the same directory as the
        given path.
        '''
        ns_path, writer = getargs('path', 'writer', kwargs)
        if writer is None:
            writer = YAMLSpecWriter(outdir=getargs('outdir', kwargs))
        ns_args = copy.copy(self.__ns_args)
        ns_args['schema'] = list()
        for ns, info in self.__namespaces.items():
            ns_args['schema'].append(info)
        for path, info in self.__sources.items():
            out = SpecFileBuilder()
            dts = list()
            for spec in info[self.__dt_key]:
                if isinstance(spec, str):
                    dts.append(spec)
                else:
                    out.add_spec(spec)
            item = {'source': path}
            if out and dts:
                raise ValueError('cannot include from source if writing to source')
            elif dts:
                item[self.__dt_key] = dts
            elif out:
                writer.write_spec(out, path)
            ns_args['schema'].append(item)
        namespace = SpecNamespace.build_namespace(**ns_args)
        writer.write_namespace(namespace, ns_path)


class SpecFileBuilder(dict):

    @docval({'name': 'spec', 'type': (GroupSpec, DatasetSpec), 'doc': 'the Spec to add'})
    def add_spec(self, **kwargs):
        spec = getargs('spec', kwargs)
        if isinstance(spec, GroupSpec):
            self.setdefault('groups', list()).append(spec)
        elif isinstance(spec, DatasetSpec):
            self.setdefault('datasets', list()).append(spec)
