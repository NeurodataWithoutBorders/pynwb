from warnings import warn
import numpy as np
from abc import ABCMeta, abstractmethod
from itertools import chain

from ..utils import docval, getargs
from ..data_utils import get_type, get_shape

from ..spec import Spec, AttributeSpec, GroupSpec, DatasetSpec
from ..spec.spec import BaseStorageSpec
from ..spec import SpecNamespace

from ..build import GroupBuilder, DatasetBuilder, LinkBuilder
from ..build.builders import BaseBuilder

from .errors import *

__valid_types = {
    'float': float,
    'float64': np.float64,
    'float32': np.float32,
    'int': int,
    'int32': np.int32,
    'int16': np.int16,
    'text': str
}

def check_type(expected, received):
    expected_type = __valid_types.get(expected)
    if expected_type is None:
        raise ValueError("Unrecognized type: '%s'" % expected)
    return expected_type is receieved

def check_shape(expected, received):
    ret = False
    if received == expected:
        ret = True
    elif received in expected:
        ret = True
    return ret

class Validator(object, metaclass=ABCMeta):

    @docval({'name': 'spec', 'type': Spec, 'doc': 'the specification to use to validate'})
    def __init__(self, **kwargs):
        self.__spec = getargs('spec', kwargs)

    @property
    def spec(self):
        return self.__spec

    @abstractmethod
    @docval({'name': 'value', 'type': None, 'doc': 'either in the form of a value or a Builder'},
            returns='a list of Errors', rtype=list)
    def validate(self, **kwargs):
        pass

class AttributeValidator(Validator):

    @docval({'name': 'spec', 'type': AttributeSpec, 'doc': 'the specification to use to validate'})
    def __init__(self, **kwargs):
        super().__init__(getargs('spec', kwargs))

    @docval({'name': 'value', 'type': None, 'doc': 'the value to validate'},
            returns='a list of Errors', rtype=list)
    def validate(self, **kwargs):
        value = getargs('value', kwargs)
        spec = self.spec
        ret = list()
        if spec.required and value is None:
            ret.append(MissingError(spec.name))
        dtype = get_type(data)
        if not check_type(self.spec.dtype, dtype):
            ret.append(DtypeError(builder.name, self.spec.dtype, dtype))
        shape = get_shape(data)
        if not check_shape(self.spec.shape, shape):
            ret.append(ShapeError(builder.name, self.spec.shape, shape))
        return ret

class BaseStorageValidator(Validator):

    @docval({'name': 'spec', 'type': BaseStorageSpec, 'doc': 'the specification to use to validate'})
    def __init__(self, **kwargs):
        super().__init__(getargs('spec', kwargs))
        self.__attribute_validators = dict()
        for attr in self.spec.attributes:
            self.__attribute_validators[attr.name] = AttributeValidator(attr)

    @docval({"name": "builder", "type": BaseBuilder, "doc": "the builder to validate"},
            returns='a list of Errors', rtype=list)
    def validate(self, **kwargs):
        builder = getargs('builder', kwargs)
        attributes = builder.attributes
        ret = list()
        for attr, validator in self.__attribute_validators.items():
            attr_val = attributes.get(attr)
            if attr_val is None:
                ret.append(MissingError(attr))
            else:
                ret.extend(validator.validate(attr_val))
        return ret

class ValidatorMap(object):

    @docval({'name': 'namespace', 'type': SpecNamespace, 'doc': 'the namespace to builder map for'})
    def __init__(self, **kwargs):
        ns = getargs('namespace', kwargs)
        self.__ns = ns
        tree = dict()
        types = ns.get_registered_types()
        for dt in types:
            spec = ns.get_spec(dt)
            parent = spec.data_type_inc
            child = spec.data_type_def
            tree.setdefault(child, list())
            if parent is not None:
                tree.setdefault(parent, list()).append(child)
        for t in tree:
            self.__rec(tree, t)
        self.__valid_types = dict()
        self.__validators = dict()
        for dt, children in tree.items():
            l = list()
            for t in children:
                spec = self.__ns.get_spec(dt)
                if isinstance(spec, GroupSpec):
                    val = GroupValidator(spec, self)
                else:
                    val = DatasetValidator(spec)
                if t == dt:
                    self.__validators[t] = val
                l.append(val)
            self.__valid_types[t] = tuple(l)

    def __rec(self, tree, node):
        if isinstance(tree[node], tuple):
            return tree[node]
        sub_types = {node}
        for child in tree[node]:
            sub_types.update(self.__rec(tree, child))
        tree[node] = tuple(sub_types)
        return tree[node]

    def valid_types(self, spec):
        try:
            return self.__valid_types[spec.data_type_def]
        except KeyError:
            raise ValueError("no children for '%s'" % spec.data_type_def)


    @docval({'name': 'data_type', 'type': str, 'doc': 'the data type to get the validator for'})
    def get_validator(self, **kwargs):
        dt = getargs('data_type', kwargs)
        try:
            return self.__validators[dt]
        except KeyError:
            msg = "data type '%s' not found in namespace %s" % (dt, self.__ns.name)
            raise ValueError(msg)

#class IncludeValidator(Validator):
#
#    @docval({'name': 'spec', 'type': BaseStorageSpec, 'doc': 'the specification to use to validate'},
#            {'name': 'valid_types', 'type': list, 'doc': 'a list of Validators of allowable types'})
#    def __init__(self, **kwargs):
#        super().__init__(getargs('spec', kwargs))
#        self.__valid_types = getargs('valid_types', kwargs)
#
#    @property
#    def valid_types(self):
#        return self.__valid_types
#
#    @docval({"name": "builder", "type": BaseBuilder, "doc": "the builder to validate"},
#            returns='a list of Errors', rtype=list)
#    def validate(self, **kwargs):
#        builder = getargs('builder', kwargs)
#        ret = list()
#        if builder is None:
#            if self.spec.required:
#                name = self.spec.name
#                if self.spec.name is None:
#                    name = self.spec.data_type_inc
#                ret.append(MissingError(name))
#        else:
#            ret.extend(self.__dt_validator.validate(builder))
#        return ret

class DatasetValidator(BaseStorageValidator):

    @docval({'name': 'spec', 'type': DatasetSpec, 'doc': 'the specification to use to validate'})
    def __init__(self, **kwargs):
        super().__init__(getargs('spec', kwargs))

    @docval({"name": "builder", "type": DatasetBuilder, "doc": "the builder to validate"},
            returns='a list of Errors', rtype=list)
    def validate(self, **kwargs):
        builder = getargs('builder', kwargs)
        ret = super().validate(builder)
        data = builder.data
        dtype = get_type(data)
        if not check_type(self.spec.dtype, dtype):
            ret.append(DtypeError(builder.name, self.spec.dtype, dtype))
        shape = get_shape(data)
        if not check_shape(self.spec.shape, shape):
            ret.append(ShapeError(builder.name, self.spec.shape, shape))
        return ret

class GroupValidator(BaseStorageValidator):

    @docval({'name': 'spec', 'type': GroupSpec, 'doc': 'the specification to use to validate'},
            {'name': 'validator_map', 'type': ValidatorMap, 'doc': 'the ValidatorMap to use during validation'})
    def __init__(self, **kwargs):
        super().__init__(getargs('spec', kwargs))
        self.__vmap = getargs('validator_map', kwargs)
        self.__include_dts = dict()
        self.__dataset_validators = dict()
        self.__group_validators = dict()
        it = chain(self.spec.datasets, self.spec.groups)
        for spec in it:
            if spec.data_type_def is None:
                if spec.data_type_inc is None:
                    if isinstance(spec, GroupSpec):
                        self.__group_validators[spec.name] = GroupValidator(spec, self.__vmap)
                    else:
                        self.__dataset_validators[spec.name] = DatasetValidator(spec)
                else:
                    self.__include_dts.append(spec.data_type_inc)
            else:
                self.__include_dts.append(spec.data_type_def)

    @docval({"name": "builder", "type": GroupBuilder, "doc": "the builder to validate"},
            returns='a list of Errors', rtype=list)
    def validate(self, **kwargs):
        builder = getargs('builder', kwargs)
        ret = super().validate(builder)
        # get the data_types
        data_types = dict()
        for key, value in builder.items():
            v_builder = value
            if isinstance(v_builder, LinkBuilder):
                v_builder = v_builder.builder
            if isinstance(v_builder, BaseBuilder):
                dt = v_builder.attributes.get(self.spec.type_key())
                if dt is not None:
                    data_types.setdefault(dt, list()).append(value)
        for dt in self.__include_dts:
            found = False
            for sub_val in self.__vmap.valid_types(dt):
                sub_dt = sub_val.data_type
                dt_builders = data_types.get(sub_dt)
                if dt_builders is not None:
                    for bldr in dt_builders:
                        sub_val.validate(bldr)
                    found = True
            if not found:
                ret.append(MissingDataType(builder.name, dt))
        it = chain(self.__dataset_validators.items(),
                   self.__group_validators.items())
        for name, validator in it:
            sub_builder = builder.get(name)
            spec = validator.spec
            if sub_builder is None:
                if spec.required:
                    ret.append(MissingError(spec.name))
            else:
                ret.extend(validator.validate(sub_builder))

        return ret
