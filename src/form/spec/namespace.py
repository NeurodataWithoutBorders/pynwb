from datetime import datetime
from copy import deepcopy, copy
import ruamel.yaml as yaml
import os.path

from ..utils import docval, getargs, popargs, get_docval
from .catalog import SpecCatalog
from .spec import GroupSpec


_namespace_args = [
    {'name': 'doc', 'type': str, 'doc': 'a description about what this namespace represents'},
    {'name': 'name', 'type': str, 'doc': 'the name of this namespace'},
    {'name': 'full_name', 'type': str, 'doc': 'extended full name of this namespace', 'default': None},
    {'name': 'version', 'type': (str, tuple, list), 'doc': 'Version number of the namespace', 'default': None},
    {'name': 'date', 'type': (datetime, str), 'doc': "Date last modified or released. Formatting is %Y-%m-%d %H:%M:%S, e.g, 2017-04-25 17:14:13",
     'default': None},
    {'name': 'author', 'type': (str, list), 'doc': 'Author or list of authors.', 'default': None},
    {'name': 'contact', 'type': (str, list), 'doc': 'List of emails. Ordering should be the same as for author', 'default': None},
    {'name': 'schema', 'type': list, 'doc': 'location of schema specification files or other Namespaces', 'default': None},
    {'name': 'catalog', 'type': SpecCatalog, 'doc': 'The SpecCatalog object for this SpecNamespace', 'default': None}
]
class SpecNamespace(dict):
    """
    A namespace for specifications
    """
    @docval(*deepcopy(_namespace_args))
    def __init__(self, **kwargs):
        doc, full_name, name, version, date, author, contact, schema, catalog  = \
            popargs('doc', 'full_name', 'name', 'version', 'date', 'author', 'contact', 'schema', 'catalog', kwargs)
        super(SpecNamespace, self).__init__()
        if doc is not None:
            self['doc'] = doc
        if full_name is not None:
            self['full_name'] = full_name
        if name is not None:
            self['name'] = name
        if version is not None:
            self['version'] = version
        if date is not None:
            self['date'] = date
        if author is not None:
            self['author'] = author
        if contact is not None:
            self['contact'] = contact
        if schema is not None:
            self['schema'] = schema
        self.__catalog = catalog if catalog is not None else SpecCatalog()

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
        return self.get('author', None)

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

    @docval({'name': 'neurodata_type', 'type': (str, type), 'doc': 'the neurodata_type to get the spec for'})
    def get_spec(self, **kwargs):
        neurodata_type = getargs('neurodata_type', **kwargs)
        self.__catalog.get_spec(neurodata_type)

    def get_registered_types(self):
        return self.__catalog.get_registered_types()

    @classmethod
    def build_namespace(cls, **spec_dict):
        kwargs = copy(spec_dict)
        try:
            args = [kwargs.pop(x['name']) for x in get_docval(cls.__init__) if 'default' not in x]
        except KeyError as e:
            raise KeyError("'%s' not found in %s" % (e.args[0], str(spec_dict)))
        return cls(*args, **kwargs)


    __loaded_specs = dict()

    @classmethod
    def __load_spec_file(cls, spec_file_path):
        ret = cls.__loaded_specs.get(spec_file_path)
        if ret is None:
            ret = dict()
            with open(spec_file_path, 'r') as stream:
                d = yaml.safe_load(stream)
                specs = d.get('specs')
                if specs is None:
                    raise ValueError("no 'specs' found in %s" % spec_file_path)
                for spec_dict in specs:
                    spec_obj = GroupSpec.build_spec(spec_dict)
                    ret[spec_obj.neurodata_type_def] = spec_obj
            cls.__loaded_specs[spec_file_path] = ret
        return ret

    @classmethod
    def __get_spec_path(cls, ns_path, spec_path):
        if os.path.isabs(spec_path):
            return spec_path
        return os.path.join(os.path.dirname(ns_path), spec_path)

    @classmethod
    def build_namespaces(cls, namespace_path, ns_catalog):
        # load namespace definition from file
        if not os.path.exists(namespace_path):
            raise FileNotFoundError("namespace file '%s' not found" % namespace_path)
        with open(namespace_path, 'r') as stream:
            d = yaml.safe_load(stream)
            namespaces = d.get('namespaces')
            if namespaces == None:
                raise ValueError("no 'namespaces' found in %s" % namespace_path)
        ret = dict()
        # now load specs into namespace
        for ns in namespaces:
            catalog = SpecCatalog()
            for s in ns['schema']:
                if 'source' in s:
                    # read specs from file
                    spec_file = cls.__get_spec_path(namespace_path, s['source'])
                    ndts = cls.__load_spec_file(spec_file).items()
                    if 'neurodata_types' in s:
                        ndts = filter(lambda k,v: k in set(s['neurodata_types']), ndts)
                    for ndt, spec in ndts:
                        catalog.auto_register(spec, spec_file)
                elif 'namespace' in s:
                    # load specs from namespace
                    try:
                        inc_ns = ns_catalog.get_namespace(s['namespace'])
                    except KeyError:
                        raise ValueError("Could not load namespace '%s'" % s['namespace'])
                    if 'neurodata_types' in s:
                        types = s['neurodata_types']
                    else:
                        types = inc_ns.get_registered_types()
                    for ndt in types:
                        spec = inc_ns.get_spec(ndt)
                        spec_file = inc_ns.catalog.get_spec_source_file(ndt)
                        catalog.auto_register(spec, spec_file)
            # construct namespace
            ret[ns['name']] = cls.build_namespace(**ns, catalog=catalog)
        return ret

#    @classmethod
#    def build_const_args(cls, spec_dict, spec_path):
#        ''' Build constructor arguments for this Spec class from a dictionary '''
#        import warnings
#        from glob import iglob
#        try:
#            import ruamel.yaml as yaml
#        except ImportError:
#            import yaml
#        from itertools import chain
#        from os.path import join
#
#        ret = super(NamespaceSpec, cls).build_const_args(spec_dict)
#        if 'author' in ret:
#            if isinstance(ret['author'], str):
#                ret['author'] = [ret['author'],]
#        if 'contact' in ret:
#            if isinstance(ret['contact'], str):
#                ret['contact'] = [ret['contact'],]
#        if 'date' in ret:
#            try:
#                ret['date'] = datetime.strptime('2017-04-25 17:14:13', "%Y-%m-%d %H:%M:%S")
#            except ValueError:
#                warnings.warn('Date for NamespaceSpec could not be converted to datetime. Storing raw string instead')
#        spec_catalog = SpecCatalog()
#        if 'schema' in ret:
#            ret.pop('schema')
#        else:
#            exts = ['yaml', 'json']
#            glob_str = join(spec_path, "*.%s")
#            for path in chain(*[iglob(glob_str % ext) for ext in exts]):
#                with open(path, 'r') as stream:
#                    for obj in yaml.safe_load(stream):
#                        if obj != 'namespaces':
#                            spec_obj = GroupSpec.build_spec(obj)
#                            spec_catalog.auto_register(spec_obj,
#                                                       source_file=path)
#        ret.__catalog = spec_catalog
#        return ret
#
#    @classmethod
#    def from_file(cls, spec_file):
#        """Build a Namespace spec from the given YAML file with the namespace definition"""
#        try:
#            import ruamel.yaml as yaml
#        except ImportError:
#            import yaml
#        from os.path import dirname
#        namespaces = []
#        with open(spec_file, 'r') as stream:
#            obj = yaml.load(stream, yaml.RoundTripLoader)
#            if 'namespaces' in obj:
#                for ns in obj['namespaces']:
#                    namespaces.append(NamespaceSpec.build_spec(ns, dirname(spec_file)))
#        if len(namespaces) == 1:
#            return namespaces[0]
#        else:
#            return namespaces
#
#    @classmethod
#    def build_spec(cls, spec_dict, spec_path):
#        """ Build a Spec object from the given Spec dict """
#        kwargs = cls.build_const_args(spec_dict, spec_path)
#        try:
#            args = [kwargs.pop(x['name']) for x in get_docval(cls.__init__) if 'default' not in x]
#        except KeyError as e:
#            raise KeyError("'%s' not found in %s" % (e.args[0], str(spec_dict)))
#        return cls(*args, **kwargs)


class NamespaceCatalog(object):

    def __init__(self):
        """Create a catalog for storing  multiple Namespaces"""
        self.__namespaces = dict()

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this namespace'},
            {'name': 'namespace', 'type': SpecNamespace, 'doc': 'the SpecNamespace object'})
    def add_namespace(self, **kwargs):
        name, namespace = getargs('name', 'namespace', kwargs)
        if name in self.__namespaces:
            raise KeyError("namespace '%s' already exists" % name)
        self.__namespaces[name] = namespace

    @docval({'name': 'name', 'type': str, 'doc': 'the name of this namespace'})
    def get_namespace(self, **kwargs):
        name = getargs('namespace', kwargs)
        ret = self.__namespaces.get(name)
        if ret is None:
            raise KeyError("'%s' not a namespace" % name)
        return ret

    @docval({'name': 'namespace', 'type': str, 'doc': 'the name of the namespace'},
            {'name': 'neurodata_type', 'type': (str, type), 'doc': 'the neurodata_type to get the spec for'},
            returns="the specification for writing the given object type to HDF5 ", rtype='Spec')
    def get_spec(self, **kwargs):
        '''
        Get the Spec object for the given type from the given Namespace
        '''
        namespace, neurodata_type = getargs('namespace', 'neurodata_type', kwargs)
        if name not in self.__namespaces:
            raise KeyError("'%s' not a namespace" % namespace)
        return self.__namespaces[namespace].get_spec(neurodata_type)

