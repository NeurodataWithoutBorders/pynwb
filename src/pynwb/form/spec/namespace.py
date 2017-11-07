from datetime import datetime
from copy import deepcopy, copy
import ruamel.yaml as yaml
import os.path
import string
from warnings import warn
from itertools import chain

from ..utils import docval, getargs, popargs, get_docval
from .catalog import SpecCatalog
from .spec import DatasetSpec, GroupSpec


_namespace_args = [
    {'name': 'doc', 'type': str, 'doc': 'a description about what this namespace represents'},
    {'name': 'name', 'type': str, 'doc': 'the name of this namespace'},
    {'name': 'schema', 'type': list, 'doc': 'location of schema specification files or other Namespaces'},
    {'name': 'full_name', 'type': str, 'doc': 'extended full name of this namespace', 'default': None},
    {'name': 'version', 'type': (str, tuple, list), 'doc': 'Version number of the namespace', 'default': None},
    {'name': 'date', 'type': (datetime, str),
     'doc': "Date last modified or released. Formatting is %Y-%m-%d %H:%M:%S, e.g, 2017-04-25 17:14:13",
     'default': None},
    {'name': 'author', 'type': (str, list), 'doc': 'Author or list of authors.', 'default': None},
    {'name': 'contact', 'type': (str, list),
     'doc': 'List of emails. Ordering should be the same as for author', 'default': None},
    {'name': 'catalog', 'type': SpecCatalog, 'doc': 'The SpecCatalog object for this SpecNamespace', 'default': None}
]


class SpecNamespace(dict):
    """
    A namespace for specifications
    """

    __types_key = 'data_types'

    @docval(*deepcopy(_namespace_args))
    def __init__(self, **kwargs):
        doc, full_name, name, version, date, author, contact, schema, catalog = \
            popargs('doc', 'full_name', 'name', 'version', 'date', 'author', 'contact', 'schema', 'catalog', kwargs)
        super(SpecNamespace, self).__init__()
        self['doc'] = doc
        self['schema'] = schema
        if any(c in string.whitespace for c in name):
            raise ValueError("'name' must not contain any whitespace")
        self['name'] = name
        if full_name is not None:
            self['full_name'] = full_name
        if version is not None:
            self['version'] = version
        if date is not None:
            self['date'] = date
        if author is not None:
            self['author'] = author
        if contact is not None:
            self['contact'] = contact
        self.__catalog = catalog if catalog is not None else SpecCatalog()

    @classmethod
    def types_key(cls):
        ''' Get the key used for specifying types to include from a file or namespace

        Override this method to use a different name for 'data_types'
        '''
        return cls.__types_key

    @property
    def full_name(self):
        """String with full name or None"""
        return self.get('full_name', None)

    @property
    def contact(self):
        """String or list of strings with the contacts or None"""
        return self.get('contact', None)

    @property
    def author(self):
        """String or list of strings with the authors or  None"""
        return self.get('author', None)

    @property
    def version(self):
        """String, list, or tuple with the version or None """
        return self.get('version', None)

    @property
    def date(self):
        """Date last modified or released.

        :return: datetime object, string, or None"""
        return self.get('full_name', None)

    @property
    def name(self):
        """String with short name or None"""
        return self.get('name', None)

    @property
    def catalog(self):
        """The SpecCatalog containing all the Specs"""
        return self.__catalog

    @docval({'name': 'data_type', 'type': (str, type), 'doc': 'the data_type to get the spec for'})
    def get_spec(self, **kwargs):
        """Get the Spec object for the given data type"""
        data_type = getargs('data_type', kwargs)
        spec = self.__catalog.get_spec(data_type)
        if spec is None:
            raise ValueError("No specification for '%s' in namespace '%s'" % (data_type, self.name))
        return spec

    @docval(returns="the a tuple of the available data types", rtype=tuple)
    def get_registered_types(self, **kwargs):
        """Get the available types in this namespace"""
        return self.__catalog.get_registered_types()

    @docval({'name': 'data_type', 'type': (str, type), 'doc': 'the data_type to get the hierarchy of'},
            returns="a tuple with the type hierarchy", rtype=tuple)
    def get_hierarchy(self, **kwargs):
        ''' Get the extension hierarchy for the given data_type in this namespace'''
        data_type = getargs('data_type', kwargs)
        return self.__catalog.get_hierarchy(data_type)

    @classmethod
    def build_namespace(cls, **spec_dict):
        kwargs = copy(spec_dict)
        try:
            args = [kwargs.pop(x['name']) for x in get_docval(cls.__init__) if 'default' not in x]
        except KeyError as e:
            raise KeyError("'%s' not found in %s" % (e.args[0], str(spec_dict)))
        return cls(*args, **kwargs)


class NamespaceCatalog(object):

    @docval({'name': 'group_spec_cls', 'type': type,
             'doc': 'the class to use for group specifications', 'default': GroupSpec},
            {'name': 'dataset_spec_cls', 'type': type,
             'doc': 'the class to use for dataset specifications', 'default': DatasetSpec},
            {'name': 'spec_namespace_cls', 'type': type,
             'doc': 'the class to use for specification namespaces', 'default': SpecNamespace},)
    def __init__(self, **kwargs):
        """Create a catalog for storing  multiple Namespaces"""
        self.__namespaces = dict()
        self.__dataset_spec_cls = getargs('dataset_spec_cls', kwargs)
        self.__group_spec_cls = getargs('group_spec_cls', kwargs)
        self.__spec_namespace_cls = getargs('spec_namespace_cls', kwargs)
        # keep track of all spec objects ever loaded, so we don't have
        # multiple object instances of a spec
        self.__loaded_specs = dict()
        self.__loaded_ns_files = dict()

    @property
    @docval(returns='a tuple of the availble namespaces', rtype=tuple)
    def namespaces(self):
        """The namespaces in this NamespaceCatalog"""
        return tuple(self.__namespaces.keys())

    @property
    def dataset_spec_cls(self):
        """The DatasetSpec class used in this NamespaceCatalog"""
        return self.__dataset_spec_cls

    @property
    def group_spec_cls(self):
        """The GroupSpec class used in this NamespaceCatalog"""
        return self.__group_spec_cls

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this namespace'},
            {'name': 'namespace', 'type': SpecNamespace, 'doc': 'the SpecNamespace object'})
    def add_namespace(self, **kwargs):
        """Add a namespace to this catalog"""
        name, namespace = getargs('name', 'namespace', kwargs)
        if name in self.__namespaces:
            raise KeyError("namespace '%s' already exists" % name)
        self.__namespaces[name] = namespace

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this namespace'},
            returns="the SpecNamespace with the given name", rtype=SpecNamespace)
    def get_namespace(self, **kwargs):
        """Get the a SpecNamespace"""
        name = getargs('name', kwargs)
        ret = self.__namespaces.get(name)
        if ret is None:
            raise KeyError("'%s' not a namespace" % name)
        return ret

    @docval({'name': 'namespace', 'type': str, 'doc': 'the name of the namespace'},
            {'name': 'data_type', 'type': (str, type), 'doc': 'the data_type to get the spec for'},
            returns="the specification for writing the given object type to HDF5 ", rtype='Spec')
    def get_spec(self, **kwargs):
        '''
        Get the Spec object for the given type from the given Namespace
        '''
        namespace, data_type = getargs('namespace', 'data_type', kwargs)
        if namespace not in self.__namespaces:
            raise KeyError("'%s' not a namespace" % namespace)
        return self.__namespaces[namespace].get_spec(data_type)

    @docval({'name': 'namespace', 'type': str, 'doc': 'the name of the namespace'},
            {'name': 'data_type', 'type': (str, type), 'doc': 'the data_type to get the spec for'},
            returns="a tuple with the type hierarchy", rtype=tuple)
    def get_hierarchy(self, **kwargs):
        '''
        Get the type hierarchy for a given data_type in a given namespace
        '''
        namespace, data_type = getargs('namespace', 'data_type', kwargs)
        spec_ns = self.__namespaces.get(namespace)
        if spec_ns is None:
            raise KeyError("'%s' not a namespace" % namespace)
        return spec_ns.get_hierarchy(data_type)

    def __load_spec_file(self, spec_file_path, catalog, dtypes=None, resolve=True):
        ret = self.__loaded_specs.get(spec_file_path)

        def __reg_spec(spec_cls, spec_dict):
            dt_def = spec_dict.get(spec_cls.def_key())
            if dt_def is None:
                msg = 'skipping spec in %s, no %s found' % (spec_file_path, spec_cls.def_key())
                warn(msg)
                return
            if dtypes and dt_def not in dtypes:
                return
            if resolve:
                self.__resolve_includes(spec_dict, catalog, spec_file_path)
            spec_obj = spec_cls.build_spec(spec_dict)
            catalog.auto_register(spec_obj, spec_file_path)
        if ret is None:
            ret = dict()
            with open(spec_file_path, 'r') as stream:
                d = yaml.safe_load(stream)
                specs = d.get('datasets', list())
                for spec_dict in specs:
                    __reg_spec(self.__dataset_spec_cls, spec_dict)
                specs = d.get('groups', list())
                for spec_dict in specs:
                    __reg_spec(self.__group_spec_cls, spec_dict)
            self.__loaded_specs[spec_file_path] = ret
        return ret

    def __resolve_includes(self, spec_dict, catalog, spec_file_path):
        """
            Pull in any attributes, datasets, or groups included
        """
        modified = False
        dt_inc = spec_dict.get(self.__group_spec_cls.inc_key())
        dt_def = spec_dict.get(self.__group_spec_cls.def_key())
        if dt_inc is not None and dt_def is not None:
            parent_spec = catalog.get_spec(dt_inc)
            if parent_spec is None:
                msg = "Cannot resolve include spec '%s' for type '%s'" % (dt_inc, dt_def)
                raise ValueError(msg)
            spec_dict[self.__group_spec_cls.inc_key()] = parent_spec
            modified = True
        it = chain(spec_dict.get('groups', list()), spec_dict.get('datasets', list()))
        for subspec_dict in it:
            sub_modified = self.__resolve_includes(subspec_dict, catalog, spec_file_path)  # noqa: F841
        return modified

    @classmethod
    def __get_spec_path(cls, ns_path, spec_path):
        if os.path.isabs(spec_path):
            return spec_path
        return os.path.join(os.path.dirname(ns_path), spec_path)

    @docval({'name': 'namespace_path', 'type': str, 'doc': 'the path to the file containing the namespaces(s) to load'},
            {'name': 'resolve', 'type': bool,
             'doc': 'whether or not to include objects from included/parent spec objects', 'default': True},
            returns='a dictionary describing the dependencies of loaded namespaces', rtype=dict)
    def load_namespaces(self, **kwargs):
        """Load the namespaces in the given file"""
        namespace_path, resolve = getargs('namespace_path', 'resolve', kwargs)
        # load namespace definition from file
        if not os.path.exists(namespace_path):
            # TODO: Fix this line for Python2
            # Raise OSError maybe?
            raise FileNotFoundError("namespace file '%s' not found" % namespace_path)  # noqa: F821
        ret = self.__loaded_ns_files.get(namespace_path)
        if ret is None:
            ret = dict()
        else:
            return ret
        with open(namespace_path, 'r') as stream:
            d = yaml.safe_load(stream)
            namespaces = d.get('namespaces')
            if namespaces is None:
                raise ValueError("no 'namespaces' found in %s" % namespace_path)
        types_key = self.__spec_namespace_cls.types_key()
        # now load specs into namespace
        for ns in namespaces:
            catalog = SpecCatalog()
            included_types = dict()
            for s in ns['schema']:
                if 'source' in s:
                    # read specs from file
                    spec_file = self.__get_spec_path(namespace_path, s['source'])
                    dtypes = None
                    if types_key in s:
                        dtypes = set(s[types_key])
                    ndts = self.__load_spec_file(spec_file, catalog, dtypes=dtypes, resolve=resolve)  # noqa: F841
                elif 'namespace' in s:
                    # load specs from namespace
                    try:
                        inc_ns = self.get_namespace(s['namespace'])
                    except KeyError:
                        raise ValueError("Could not load namespace '%s'" % s['namespace'])
                    if types_key in s:
                        types = s[types_key]
                    else:
                        types = inc_ns.get_registered_types()
                    for ndt in types:
                        spec = inc_ns.get_spec(ndt)
                        spec_file = inc_ns.catalog.get_spec_source_file(ndt)
                        catalog.register_spec(spec, spec_file)
                    included_types[s['namespace']] = tuple(types)
            ret[ns['name']] = included_types
            # construct namespace
            self.add_namespace(ns['name'], self.__spec_namespace_cls.build_namespace(catalog=catalog, **ns))
        self.__loaded_ns_files[namespace_path] = ret
        return ret
