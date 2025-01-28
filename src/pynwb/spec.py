from copy import copy, deepcopy

from hdmf.spec import (LinkSpec, GroupSpec, DatasetSpec, SpecNamespace, NamespaceBuilder,
                       AttributeSpec, DtypeSpec, RefSpec)
from hdmf.spec.write import export_spec  # noqa: F401
from hdmf.utils import docval, get_docval

from . import CORE_NAMESPACE


def __swap_inc_def(cls):
    args = get_docval(cls.__init__)
    clsname = 'NWB%s' % cls.__name__
    ret = list()
    # do not set default neurodata_type_inc for base hdmf-common types that should not have data_type_inc
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

    @docval(*deepcopy(_ref_docval))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


_attr_docval = __swap_inc_def(AttributeSpec)


class NWBAttributeSpec(AttributeSpec):

    @docval(*deepcopy(_attr_docval))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


_link_docval = __swap_inc_def(LinkSpec)


class NWBLinkSpec(LinkSpec):

    @docval(*deepcopy(_link_docval))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def neurodata_type_inc(self):
        ''' The neurodata type of target specification '''
        return self.data_type_inc


class BaseStorageOverride:
    ''' This class is used for the purpose of overriding
        :py:class:`~hdmf.spec.spec.BaseStorageSpec` classmethods, without creating diamond
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
        proxy = super()
        if proxy.inc_key() in spec_dict:
            spec_dict[cls.inc_key()] = spec_dict.pop(proxy.inc_key())
        if proxy.def_key() in spec_dict:
            spec_dict[cls.def_key()] = spec_dict.pop(proxy.def_key())
        ret = proxy.build_const_args(spec_dict)
        return ret

    @classmethod
    def _translate_kwargs(cls, kwargs):
        """Swap neurodata_type_def and neurodata_type_inc for data_type_def and data_type_inc, respectively"""
        proxy = super()
        kwargs[proxy.def_key()] = kwargs.pop(cls.def_key())
        kwargs[proxy.inc_key()] = kwargs.pop(cls.inc_key())
        return kwargs


_dtype_docval = __swap_inc_def(DtypeSpec)


class NWBDtypeSpec(DtypeSpec):

    @docval(*deepcopy(_dtype_docval))
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


_dataset_docval = __swap_inc_def(DatasetSpec)


class NWBDatasetSpec(BaseStorageOverride, DatasetSpec):
    ''' The Spec class to use for NWB dataset specifications.

    Classes will automatically include NWBData if None is specified.
    '''

    @docval(*deepcopy(_dataset_docval))
    def __init__(self, **kwargs):
        kwargs = self._translate_kwargs(kwargs)
        # set data_type_inc to NWBData only if it is not specified and the type is not an HDMF base type
        if kwargs['data_type_inc'] is None and kwargs['data_type_def'] not in (None, 'Data'):
            kwargs['data_type_inc'] = 'NWBData'
        super().__init__(**kwargs)


_group_docval = __swap_inc_def(GroupSpec)


class NWBGroupSpec(BaseStorageOverride, GroupSpec):
    ''' The Spec class to use for NWB group specifications.

    Classes will automatically include NWBContainer if None is specified.
    '''

    @docval(*deepcopy(_group_docval))
    def __init__(self, **kwargs):
        kwargs = self._translate_kwargs(kwargs)
        # set data_type_inc to NWBData only if it is not specified and the type is not an HDMF base type
        # NOTE: CSRMatrix in hdmf-common-schema does not have a data_type_inc but should not inherit from
        # NWBContainer. This will be fixed in hdmf-common-schema 1.2.1.
        if kwargs['data_type_inc'] is None and kwargs['data_type_def'] not in (None, 'Container', 'CSRMatrix'):
            kwargs['data_type_inc'] = 'NWBContainer'
        super().__init__(**kwargs)

    @classmethod
    def dataset_spec_cls(cls):
        return NWBDatasetSpec

    @docval({'name': 'neurodata_type', 'type': str, 'doc': 'the neurodata_type to retrieve'})
    def get_neurodata_type(self, **kwargs):
        ''' Get a specification by "neurodata_type" '''
        return super().get_data_type(kwargs['neurodata_type'])

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
        super().__init__(**kwargs)
        self.include_namespace(CORE_NAMESPACE)
