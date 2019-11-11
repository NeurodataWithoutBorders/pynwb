from copy import copy, deepcopy

from hdmf.spec import LinkSpec, GroupSpec, DatasetSpec, SpecNamespace,\
                       NamespaceBuilder, AttributeSpec, DtypeSpec, RefSpec
from hdmf.spec.write import export_spec  # noqa: F401
from hdmf.utils import docval, get_docval, call_docval_func

from . import CORE_NAMESPACE


def __swap_inc_def(cls):
    args = get_docval(cls.__init__)
    clsname = 'NWB%s' % cls.__name__
    ret = list()
    for arg in args:
        if arg['name'] == 'data_type_def':
            ret.append({'name': 'neurodata_type_def', 'type': str,
                        'doc': 'the NWB data type this spec defines', 'default': None})
        elif arg['name'] == 'data_type_inc':
            ret.append({'name': 'neurodata_type_inc', 'type': (clsname, str),
                        'doc': 'the NWB data type this spec includes', 'default': None})
        else:
            ret.append(copy(arg))
    return ret


_ref_docval = __swap_inc_def(RefSpec)


class NWBRefSpec(RefSpec):

    @docval(*_ref_docval)
    def __init__(self, **kwargs):
        call_docval_func(super(NWBRefSpec, self).__init__, kwargs)


_attr_docval = __swap_inc_def(AttributeSpec)


class NWBAttributeSpec(AttributeSpec):

    @docval(*_attr_docval)
    def __init__(self, **kwargs):
        call_docval_func(super(NWBAttributeSpec, self).__init__, kwargs)


_link_docval = __swap_inc_def(LinkSpec)


class NWBLinkSpec(LinkSpec):

    @docval(*_link_docval)
    def __init__(self, **kwargs):
        call_docval_func(super(NWBLinkSpec, self).__init__, kwargs)

    @property
    def neurodata_type_inc(self):
        ''' The neurodata type of target specification '''
        return self.data_type_inc


class BaseStorageOverride(object):
    ''' This class is used for the purpose of overriding
        BaseStorageSpec classmethods, without creating diamond
        inheritance hierarchies.
    '''

    __type_key = 'neurodata_type'
    __inc_key = 'neurodata_type_inc'
    __def_key = 'neurodata_type_def'

    @classmethod
    def type_key(cls):
        ''' Get the key used to store data type on an instance'''
        return cls.__type_key

    @classmethod
    def inc_key(cls):
        ''' Get the key used to define a data_type include.'''
        return cls.__inc_key

    @classmethod
    def def_key(cls):
        ''' Get the key used to define a data_type definition.'''
        return cls.__def_key

    @property
    def neurodata_type_inc(self):
        return self.data_type_inc

    @property
    def neurodata_type_def(self):
        return self.data_type_def

    @classmethod
    def build_const_args(cls, spec_dict):
        """Extend base functionality to remap data_type_def and data_type_inc keys"""
        spec_dict = copy(spec_dict)
        proxy = super(BaseStorageOverride, cls)
        if proxy.inc_key() in spec_dict:
            spec_dict[cls.inc_key()] = spec_dict.pop(proxy.inc_key())
        if proxy.def_key() in spec_dict:
            spec_dict[cls.def_key()] = spec_dict.pop(proxy.def_key())
        ret = proxy.build_const_args(spec_dict)
        return ret

    @classmethod
    def _translate_kwargs(cls, kwargs):
        """Swap neurodata_type_def and neurodata_type_inc for data_type_def and data_type_inc, respectively"""
        proxy = super(BaseStorageOverride, cls)
        kwargs[proxy.def_key()] = kwargs.pop(cls.def_key())
        kwargs[proxy.inc_key()] = kwargs.pop(cls.inc_key())
        args = [kwargs.pop(x['name']) for x in get_docval(proxy.__init__) if 'default' not in x]
        return args, kwargs


_dtype_docval = __swap_inc_def(DtypeSpec)


class NWBDtypeSpec(DtypeSpec):

    @docval(*_dtype_docval)
    def __init__(self, **kwargs):
        call_docval_func(super(NWBDtypeSpec, self).__init__, kwargs)


_dataset_docval = __swap_inc_def(DatasetSpec)


class NWBDatasetSpec(BaseStorageOverride, DatasetSpec):
    ''' The Spec class to use for NWB specifications '''

    @docval(*_dataset_docval)
    def __init__(self, **kwargs):
        args, kwargs = self._translate_kwargs(kwargs)
        super(NWBDatasetSpec, self).__init__(*args, **kwargs)


_group_docval = __swap_inc_def(GroupSpec)


class NWBGroupSpec(BaseStorageOverride, GroupSpec):
    ''' The Spec class to use for NWB specifications '''

    @docval(*_group_docval)
    def __init__(self, **kwargs):
        args, kwargs = self._translate_kwargs(kwargs)
        super(NWBGroupSpec, self).__init__(*args, **kwargs)

    @classmethod
    def dataset_spec_cls(cls):
        return NWBDatasetSpec

    @docval({'name': 'neurodata_type', 'type': str, 'doc': 'the neurodata_type to retrieve'})
    def get_neurodata_type(self, **kwargs):
        '''
        Get a specification by "data_type"
        '''
        return super(NWBGroupSpec, self).get_data_type(kwargs['neurodata_type'])

    @docval(*deepcopy(_group_docval))
    def add_group(self, **kwargs):
        ''' Add a new specification for a subgroup to this group specification '''
        doc = kwargs.pop('doc')
        spec = NWBGroupSpec(doc, **kwargs)
        self.set_group(spec)
        return spec

    @docval(*deepcopy(_dataset_docval))
    def add_dataset(self, **kwargs):
        ''' Add a new specification for a subgroup to this group specification '''
        doc = kwargs.pop('doc')
        spec = NWBDatasetSpec(doc, **kwargs)
        self.set_dataset(spec)
        return spec


class NWBNamespace(SpecNamespace):
    '''
    A Namespace class for NWB
    '''

    __types_key = 'neurodata_types'

    @classmethod
    def types_key(cls):
        return cls.__types_key


class NWBNamespaceBuilder(NamespaceBuilder):
    '''
    A class for writing namespace and spec files for extensions of types in
    the NWB core namespace
    '''

    @docval({'name': 'doc', 'type': str, 'doc': 'a description about what this namespace represents'},
            {'name': 'name', 'type': str, 'doc': 'the name of this namespace'},
            {'name': 'full_name', 'type': str, 'doc': 'extended full name of this namespace', 'default': None},
            {'name': 'version', 'type': (str, tuple, list), 'doc': 'Version number of the namespace', 'default': None},
            {'name': 'author', 'type': (str, list), 'doc': 'Author or list of authors.', 'default': None},
            {'name': 'contact', 'type': (str, list),
             'doc': 'List of emails. Ordering should be the same as for author', 'default': None})
    def __init__(self, **kwargs):
        ''' Create a NWBNamespaceBuilder '''
        kwargs['namespace_cls'] = NWBNamespace
        call_docval_func(super(NWBNamespaceBuilder, self).__init__, kwargs)
        self.include_namespace(CORE_NAMESPACE)
