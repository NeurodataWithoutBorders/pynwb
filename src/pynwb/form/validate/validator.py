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

from .errors import *  # noqa: F403
from six import with_metaclass, raise_from

__valid_dtypes = {
    'float': float,
    'float64': np.float64,
    'float32': np.float32,
    'int': int,
    'int32': np.int32,
    'int16': np.int16,
    'text': str,
    'str': str
}


def check_type(expected, received):
    expected_type = __valid_dtypes.get(expected)
    if expected_type is None:
        raise ValueError("Unrecognized type: '%s'" % expected)
    return expected_type is received


def check_shape(expected, received):
    ret = False
    if received == expected:
        ret = True
    elif received in expected:
        ret = True
    return ret


class Validator(with_metaclass(ABCMeta, object)):
    '''A base class for classes that will be used to validate against Spec subclasses'''

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
    '''A class for validating values against AttributeSpecs'''

    @docval({'name': 'spec', 'type': AttributeSpec, 'doc': 'the specification to use to validate'})
    def __init__(self, **kwargs):
        super(AttributeValidator, self).__init__(getargs('spec', kwargs))

    @docval({'name': 'value', 'type': None, 'doc': 'the value to validate'},
            returns='a list of Errors', rtype=list)
    def validate(self, **kwargs):
        value = getargs('value', kwargs)
        spec = self.spec
        ret = list()
        if spec.required and value is None:
            ret.append(MissingError(spec.name))  # noqa: F405
        else:
            dtype = get_type(value)
            if not check_type(spec.dtype, dtype):
                ret.append(DtypeError(spec.name, spec.dtype, dtype))  # noqa: F405
            shape = get_shape(value)
            if not check_shape(spec.shape, shape):
                ret.append(ShapeError(spec.name, spec.shape, shape))  # noqa: F405
        return ret


class BaseStorageValidator(Validator):
    '''A base class for validating against Spec objects that have attributes i.e. BaseStorageSpec'''

    @docval({'name': 'spec', 'type': BaseStorageSpec, 'doc': 'the specification to use to validate'})
    def __init__(self, **kwargs):
        super(BaseStorageValidator, self).__init__(getargs('spec', kwargs))
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
                if validator.spec.required:
                    ret.append(MissingError(attr))  # noqa: F405
            else:
                ret.extend(validator.validate(attr_val))
        return ret


class ValidatorMap(object):
    """A class for keeping track of Validator objects for all data types in a namespace"""

    @docval({'name': 'namespace', 'type': SpecNamespace, 'doc': 'the namespace to builder map for'})
    def __init__(self, **kwargs):
        ns = getargs('namespace', kwargs)
        self.__ns = ns
        tree = dict()
        types = ns.get_registered_types()
        self.__type_key = ns.get_spec(types[0]).type_key()
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
            _list = list()
            for t in children:
                spec = self.__ns.get_spec(dt)
                if isinstance(spec, GroupSpec):
                    val = GroupValidator(spec, self)
                else:
                    val = DatasetValidator(spec)
                if t == dt:
                    self.__validators[t] = val
                _list.append(val)
            self.__valid_types[t] = tuple(_list)

    def __rec(self, tree, node):
        if isinstance(tree[node], tuple):
            return tree[node]
        sub_types = {node}
        for child in tree[node]:
            sub_types.update(self.__rec(tree, child))
        tree[node] = tuple(sub_types)
        return tree[node]

    @docval({'name': 'spec', 'type': (Spec, str), 'doc': 'the specification to use to validate'},
            returns='all valid sub data types for the given spec', rtype=tuple)
    def valid_types(self, **kwargs):
        '''Get all valid types for a given data type'''
        spec = getargs('spec', kwargs)
        if isinstance(spec, Spec):
            spec = spec.data_type_def
        try:
            return self.__valid_types[spec]
        except KeyError:
            raise_from(ValueError("no children for '%s'" % spec), None)

    @docval({'name': 'data_type', 'type': (BaseStorageSpec, str),
             'doc': 'the data type to get the validator for'},
            returns='the validator ``data_type``', rtype=BaseStorageValidator)
    def get_validator(self, **kwargs):
        """Return the validator for a given data type"""
        dt = getargs('data_type', kwargs)
        if isinstance(dt, BaseStorageSpec):
            dt_tmp = dt.data_type_def
            if dt_tmp is None:
                dt_tmp = dt.data_type_inc
            dt = dt_tmp
        try:
            return self.__validators[dt]
        except KeyError:
            msg = "data type '%s' not found in namespace %s" % (dt, self.__ns.name)
            raise_from(ValueError(msg), None)

    @docval({'name': 'builder', 'type': BaseBuilder, 'doc': 'the builder to validate'},
            returns="a list of errors found", rtype=list)
    def validate(self, **kwargs):
        """Validate a builder against a Spec

        ``builder`` must have the attribute used to specifying data type
        by the namespace used to construct this ValidatorMap.
        """
        builder = getargs('builder', kwargs)
        dt = builder.attributes.get(self.__type_key)
        if dt is None:
            msg = "builder must have data type defined with attribute '%s'" % self.__type_key
            raise ValueError(msg)
        validator = self.get_validator(dt)
        return validator.validate(builder)


class DatasetValidator(BaseStorageValidator):
    '''A class for validating DatasetBuilders against DatasetSpecs'''

    @docval({'name': 'spec', 'type': DatasetSpec, 'doc': 'the specification to use to validate'})
    def __init__(self, **kwargs):
        super(DatasetValidator, self).__init__(getargs('spec', kwargs))

    @docval({"name": "builder", "type": DatasetBuilder, "doc": "the builder to validate"},
            returns='a list of Errors', rtype=list)
    def validate(self, **kwargs):
        builder = getargs('builder', kwargs)
        ret = super(DatasetValidator, self).validate(builder)
        data = builder.data
        dtype = get_type(data)
        if not check_type(self.spec.dtype, dtype):
            ret.append(DtypeError(builder.name, self.spec.dtype, dtype))  # noqa: F405
        shape = get_shape(data)
        if not check_shape(self.spec.shape, shape):
            ret.append(ShapeError(builder.name, self.spec.shape, shape))  # noqa: F405
        return ret


class GroupValidator(BaseStorageValidator):
    '''A class for validating GroupBuilders against GroupSpecs'''

    @docval({'name': 'spec', 'type': GroupSpec, 'doc': 'the specification to use to validate'},
            {'name': 'validator_map', 'type': ValidatorMap, 'doc': 'the ValidatorMap to use during validation'})
    def __init__(self, **kwargs):
        super(GroupValidator, self).__init__(getargs('spec', kwargs))
        self.__vmap = getargs('validator_map', kwargs)
        self.__include_dts = list()
        self.__dataset_validators = dict()
        self.__group_validators = dict()
        it = chain(self.spec.datasets, self.spec.groups)
        for spec in it:
            dt = None
            if spec.data_type_def is None:
                if spec.data_type_inc is None:
                    if isinstance(spec, GroupSpec):
                        self.__group_validators[spec.name] = GroupValidator(spec, self.__vmap)
                    else:
                        self.__dataset_validators[spec.name] = DatasetValidator(spec)
                else:
                    dt = spec.data_type_inc
                    self.__include_dts.append(spec.data_type_inc)
            else:
                dt = spec.data_type_def
                self.__include_dts.append(spec.data_type_def)
            if dt is not None:
                if spec.name is not None:
                    # validator = self.__vmap.get_validator(dt)
                    if isinstance(spec, GroupSpec):
                        self.__group_validators[spec.name] = spec
                    else:
                        self.__dataset_validators[spec.name] = spec
                else:
                    self.__include_dts.append(dt)

    @docval({"name": "builder", "type": GroupBuilder, "doc": "the builder to validate"},
            returns='a list of Errors', rtype=list)
    def validate(self, **kwargs):
        builder = getargs('builder', kwargs)
        ret = super(GroupValidator, self).validate(builder)
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
                spec = sub_val.spec
                sub_dt = spec.data_type_def
                dt_builders = data_types.get(sub_dt)
                if dt_builders is not None:
                    if spec.name is not None:
                        dt_builders = filter(lambda x: x.name == spec.name, dt_builder)  # noqa: F405
                    for bldr in dt_builders:
                        sub_val.validate(bldr)
                    found = True
            if not found:
                ret.append(MissingDataType(builder.name, dt))  # noqa: F405
        it = chain(self.__dataset_validators.items(),
                   self.__group_validators.items())
        for name, validator in it:
            sub_builder = builder.get(name)
            if isinstance(validator, BaseStorageSpec):
                inc_spec = validator
                validator = self.__vmap.get_validator(inc_spec)
                def_spec = validator.spec
                if sub_builder is None:
                    if inc_spec.required:
                        ret.append(MissingDataType(builder.name, def_spec.data_type_def))  # noqa: F405
                else:
                    ret.extend(validator.validate(sub_builder))

            else:
                spec = validator.spec
                if sub_builder is None:
                    if spec.required:
                        ret.append(MissingError(spec.name))  # noqa: F405
                else:
                    ret.extend(validator.validate(sub_builder))

        return ret
