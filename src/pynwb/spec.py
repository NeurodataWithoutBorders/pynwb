from copy import copy, deepcopy

from form.spec import LinkSpec, GroupSpec, DatasetSpec, SpecNamespace
from form.utils import docval, get_docval, getargs


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
        ''' Get the key used to store data type on an instance

        Override this method to use a different name for 'data_type'
        '''
        return cls.__type_key

    @classmethod
    def inc_key(cls):
        ''' Get the key used to define a data_type include.

        Override this method to use a different keyword for 'data_type_inc'
        '''
        return cls.__inc_key

    @classmethod
    def def_key(cls):
        ''' Get the key used to define a data_type definition.

        Override this method to use a different keyword for 'data_type_def'
        '''
        return cls.__def_key

    @property
    def neurodata_type(self):
        return self.data_type

    @property
    def neurodata_type_inc(self):
        return self.data_type_inc

    @property
    def neurodata_type_def(self):
        return self.data_type_def


def __swap_inc_def(cls):
    args = get_docval(cls.__init__)
    clsname = 'NWB%s' % cls.__name__
    ret = list()
    for arg in args:
        if arg['name'] == 'data_type_def':
            ret.append({'name': 'neurodata_type_def', 'type': str, 'doc': 'the NWB data type this spec defines', 'default': None})
        elif arg['name'] == 'data_type_inc':
            ret.append({'name': 'neurodata_type_inc', 'type': (clsname, str), 'doc': 'the NWB data type this spec includes', 'default': None})
        else:
            ret.append(copy(arg))
    return ret

#_dataset_docval = __swap_inc_def(get_docval(DatasetSpec.__init__))
_dataset_docval = __swap_inc_def(DatasetSpec)
class NWBDatasetSpec(BaseStorageOverride, DatasetSpec):
    ''' The Spec class to use for NWB specifications '''

    @staticmethod
    def translate_kwargs(kwargs):
        kwargs[DatasetSpec.def_key()] = kwargs.pop(BaseStorageOverride.def_key())
        kwargs[DatasetSpec.inc_key()] = kwargs.pop(BaseStorageOverride.inc_key())
        args = [kwargs.pop(x['name']) for x in get_docval(DatasetSpec.__init__) if 'default' not in x]
        return args, kwargs

    @docval(*_dataset_docval)
    def __init__(self, **kwargs):
        args, kwargs = self.translate_kwargs(kwargs)
        super(NWBDatasetSpec, self).__init__(*args, **kwargs)


#_group_docval = __swap_inc_def(get_docval(GroupSpec.__init__))
_group_docval = __swap_inc_def(GroupSpec)
class NWBGroupSpec(BaseStorageOverride, GroupSpec):
    ''' The Spec class to use for NWB specifications '''
    #TODO: add unit tests for this

    @staticmethod
    def translate_kwargs(kwargs):
        kwargs[GroupSpec.def_key()] = kwargs.pop(BaseStorageOverride.def_key())
        kwargs[GroupSpec.inc_key()] = kwargs.pop(BaseStorageOverride.inc_key())
        args = [kwargs.pop(x['name']) for x in get_docval(GroupSpec.__init__) if 'default' not in x]
        return args, kwargs

    @docval(*_group_docval)
    def __init__(self, **kwargs):
        args, kwargs = self.translate_kwargs(kwargs)
        super(NWBGroupSpec, self).__init__(*args, **kwargs)

    @classmethod
    def dataset_spec_cls(cls):
        return NWBDatasetSpec

    @docval({'name': 'neurodata_type', 'type': str, 'doc': 'the neurodata_type to retrieve'})
    def get_neurodata_type(self, **kwargs):
        '''
        Get a specification by "data_type"
        '''
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

    __types_key = 'neurodata_types'

    @classmethod
    def types_key(cls):
        return cls.__types_key

