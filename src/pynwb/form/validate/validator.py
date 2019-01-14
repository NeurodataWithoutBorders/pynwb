import numpy as np
from abc import ABCMeta, abstractmethod
from copy import copy
import re
from itertools import chain

from ..utils import docval, getargs, call_docval_func, pystr
from ..data_utils import get_shape

from ..spec import Spec, AttributeSpec, GroupSpec, DatasetSpec, RefSpec
from ..spec.spec import BaseStorageSpec, DtypeHelper
from ..spec import SpecNamespace

from ..build import GroupBuilder, DatasetBuilder, LinkBuilder, ReferenceBuilder, RegionBuilder
from ..build.builders import BaseBuilder

from .errors import Error, DtypeError, MissingError, MissingDataType, ShapeError, IllegalLinkError, IncorrectDataType
from six import with_metaclass, raise_from, text_type, binary_type


__synonyms = DtypeHelper.primary_dtype_synonyms

__additional = {
    'float': ['double'],
    'int8': ['short', 'int', 'long'],
    'short': ['int', 'long'],
    'int': ['long'],
    'uint8': ['uint16', 'uint32', 'uint64'],
    'uint16': ['uint32', 'uint64'],
    'uint32': ['uint64'],
}

__allowable = dict()
for dt, dt_syn in __synonyms.items():
    allow = copy(dt_syn)
    if dt in __additional:
        for addl in __additional[dt]:
            allow.extend(__synonyms[addl])
    for syn in dt_syn:
        __allowable[syn] = allow
__allowable['numeric'] = set(chain.from_iterable(__allowable[k] for k in __allowable if 'int' in k or 'float' in k))


def check_type(expected, received):
    '''
    *expected* should come from the spec
    *received* should come from the data
    '''
    if isinstance(expected, list):
        if len(expected) > len(received):
            raise ValueError('compound type shorter than expected')
        for i, exp in enumerate(DtypeHelper.simplify_cpd_type(expected)):
            rec = received[i]
            if rec not in __allowable[exp]:
                return False
        return True
    else:
        if isinstance(received, np.dtype):
            if received.char == 'O':
                if 'vlen' in received.metadata:
                    received = received.metadata['vlen']
                else:
                    raise ValueError("Unrecognized type: '%s'" % received)
                received = 'utf' if received is text_type else 'ascii'
            elif received.char == 'U':
                received = 'utf'
            elif received.char == 'S':
                received = 'ascii'
            else:
                received = received.name
        elif isinstance(received, type):
            received = received.__name__
        if isinstance(expected, RefSpec):
            expected = expected.reftype
        elif isinstance(expected, type):
            expected = expected.__name__
        return received in __allowable[expected]


def get_iso8601_regex():
    isodate_re = (r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):'
                  r'([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$')
    return re.compile(isodate_re)


_iso_re = get_iso8601_regex()


def _check_isodatetime(s, default=None):
    try:
        if _iso_re.match(pystr(s)) is not None:
            return 'isodatetime'
    except Exception:
        pass
    return default


def get_type(data):
    if isinstance(data, text_type):
        return _check_isodatetime(data, 'utf')
    elif isinstance(data, binary_type):
        return _check_isodatetime(data, 'ascii')
    elif isinstance(data, RegionBuilder):
        return 'region'
    elif isinstance(data, ReferenceBuilder):
        return 'object'
    elif isinstance(data, np.ndarray):
        return get_type(data[0])
    if not hasattr(data, '__len__'):
        return type(data).__name__
    else:
        if hasattr(data, 'dtype'):
            return data.dtype
        if len(data) == 0:
            raise ValueError('cannot determine type for empty data')
        return get_type(data[0])


def check_shape(expected, received):
    ret = False
    if expected is None:
        ret = True
    else:
        if isinstance(expected, (list, tuple)):
            if isinstance(expected[0], (list, tuple)):
                for sub in expected:
                    if check_shape(sub, received):
                        ret = True
                        break
            else:
                if len(expected) == len(received):
                    ret = True
                    for e, r in zip(expected, received):
                        if not check_shape(e, r):
                            ret = False
                            break
        elif isinstance(expected, int):
            ret = expected == received
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
                spec = self.__ns.get_spec(t)
                if isinstance(spec, GroupSpec):
                    val = GroupValidator(spec, self)
                else:
                    val = DatasetValidator(spec, self)
                if t == dt:
                    self.__validators[t] = val
                _list.append(val)
            self.__valid_types[dt] = tuple(_list)

    def __rec(self, tree, node):
        if isinstance(tree[node], tuple):
            return tree[node]
        sub_types = {node}
        for child in tree[node]:
            sub_types.update(self.__rec(tree, child))
        tree[node] = tuple(sub_types)
        return tree[node]

    @property
    def namespace(self):
        return self.__ns

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
            returns='the validator ``data_type``')
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


class Validator(with_metaclass(ABCMeta, object)):
    '''A base class for classes that will be used to validate against Spec subclasses'''

    @docval({'name': 'spec', 'type': Spec, 'doc': 'the specification to use to validate'},
            {'name': 'validator_map', 'type': ValidatorMap, 'doc': 'the ValidatorMap to use during validation'})
    def __init__(self, **kwargs):
        self.__spec = getargs('spec', kwargs)
        self.__vmap = getargs('validator_map', kwargs)

    @property
    def spec(self):
        return self.__spec

    @property
    def vmap(self):
        return self.__vmap

    @abstractmethod
    @docval({'name': 'value', 'type': None, 'doc': 'either in the form of a value or a Builder'},
            returns='a list of Errors', rtype=list)
    def validate(self, **kwargs):
        pass

    @classmethod
    def get_spec_loc(cls, spec):
        stack = list()
        tmp = spec
        while tmp is not None:
            name = tmp.name
            if name is None:
                name = tmp.data_type_def
                if name is None:
                    name = tmp.data_type_inc
            stack.append(name)
            tmp = tmp.parent
        return "/".join(reversed(stack))

    @classmethod
    def get_builder_loc(cls, builder):
        stack = list()
        tmp = builder
        while tmp is not None and tmp.name != 'root':
            stack.append(tmp.name)
            tmp = tmp.parent
        return "/".join(reversed(stack))


class AttributeValidator(Validator):
    '''A class for validating values against AttributeSpecs'''

    @docval({'name': 'spec', 'type': AttributeSpec, 'doc': 'the specification to use to validate'},
            {'name': 'validator_map', 'type': ValidatorMap, 'doc': 'the ValidatorMap to use during validation'})
    def __init__(self, **kwargs):
        call_docval_func(super(AttributeValidator, self).__init__, kwargs)

    @docval({'name': 'value', 'type': None, 'doc': 'the value to validate'},
            returns='a list of Errors', rtype=list)
    def validate(self, **kwargs):
        value = getargs('value', kwargs)
        ret = list()
        spec = self.spec
        if spec.required and value is None:
            ret.append(MissingError(self.get_spec_loc(spec)))
        else:
            if spec.dtype is None:
                ret.append(Error(self.get_spec_loc(spec)))
            elif isinstance(spec.dtype, RefSpec):
                if not isinstance(value, BaseBuilder):
                    expected = '%s reference' % spec.dtype.reftype
                    ret.append(DtypeError(self.get_spec_loc(spec), expected, get_type(value)))
                else:
                    target_spec = self.vmap.namespace.catalog.get_spec(spec.dtype.target_type)
                    data_type = value.attributes.get(target_spec.type_key())
                    hierarchy = self.vmap.namespace.catalog.get_hierarchy(data_type)
                    if spec.dtype.target_type not in hierarchy:
                        ret.append(IncorrectDataType(self.get_spec_loc(spec), spec.dtype.target_type, data_type))
            else:
                dtype = get_type(value)
                if not check_type(spec.dtype, dtype):
                    ret.append(DtypeError(self.get_spec_loc(spec), spec.dtype, dtype))
            shape = get_shape(value)
            if not check_shape(spec.shape, shape):
                ret.append(ShapeError(self.get_spec_loc(spec), spec.shape, shape))
        return ret


class BaseStorageValidator(Validator):
    '''A base class for validating against Spec objects that have attributes i.e. BaseStorageSpec'''

    @docval({'name': 'spec', 'type': BaseStorageSpec, 'doc': 'the specification to use to validate'},
            {'name': 'validator_map', 'type': ValidatorMap, 'doc': 'the ValidatorMap to use during validation'})
    def __init__(self, **kwargs):
        call_docval_func(super(BaseStorageValidator, self).__init__, kwargs)
        self.__attribute_validators = dict()
        for attr in self.spec.attributes:
            self.__attribute_validators[attr.name] = AttributeValidator(attr, self.vmap)

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
                    ret.append(MissingError(self.get_spec_loc(validator.spec),
                                            location=self.get_builder_loc(builder)))
            else:
                errors = validator.validate(attr_val)
                for err in errors:
                    err.location = self.get_builder_loc(builder) + ".%s" % validator.spec.name
                ret.extend(errors)
        return ret


class DatasetValidator(BaseStorageValidator):
    '''A class for validating DatasetBuilders against DatasetSpecs'''

    @docval({'name': 'spec', 'type': DatasetSpec, 'doc': 'the specification to use to validate'},
            {'name': 'validator_map', 'type': ValidatorMap, 'doc': 'the ValidatorMap to use during validation'})
    def __init__(self, **kwargs):
        call_docval_func(super(DatasetValidator, self).__init__, kwargs)

    @docval({"name": "builder", "type": DatasetBuilder, "doc": "the builder to validate"},
            returns='a list of Errors', rtype=list)
    def validate(self, **kwargs):
        builder = getargs('builder', kwargs)
        ret = super(DatasetValidator, self).validate(builder)
        data = builder.data
        if self.spec.dtype is not None:
            dtype = get_type(data)
            if not check_type(self.spec.dtype, dtype):
                ret.append(DtypeError(self.get_spec_loc(self.spec), self.spec.dtype, dtype,
                                      location=self.get_builder_loc(builder)))
        shape = get_shape(data)
        if not check_shape(self.spec.shape, shape):
            ret.append(ShapeError(self.get_spec_loc(self.spec), self.spec.shape, shape,
                                  location=self.get_builder_loc(builder)))
        return ret


class GroupValidator(BaseStorageValidator):
    '''A class for validating GroupBuilders against GroupSpecs'''

    @docval({'name': 'spec', 'type': GroupSpec, 'doc': 'the specification to use to validate'},
            {'name': 'validator_map', 'type': ValidatorMap, 'doc': 'the ValidatorMap to use during validation'})
    def __init__(self, **kwargs):
        call_docval_func(super(GroupValidator, self).__init__, kwargs)
        self.__include_dts = dict()
        self.__dataset_validators = dict()
        self.__group_validators = dict()
        it = chain(self.spec.datasets, self.spec.groups)
        for spec in it:
            if spec.data_type_def is None:
                if spec.data_type_inc is None:
                    if isinstance(spec, GroupSpec):
                        self.__group_validators[spec.name] = GroupValidator(spec, self.vmap)
                    else:
                        self.__dataset_validators[spec.name] = DatasetValidator(spec, self.vmap)
                else:
                    self.__include_dts[spec.data_type_inc] = spec
            else:
                self.__include_dts[spec.data_type_def] = spec

    @docval({"name": "builder", "type": GroupBuilder, "doc": "the builder to validate"},    # noqa: C901
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
        for dt, inc_spec in self.__include_dts.items():
            found = False
            inc_name = inc_spec.name
            for sub_val in self.vmap.valid_types(dt):
                spec = sub_val.spec
                sub_dt = spec.data_type_def
                dt_builders = data_types.get(sub_dt)
                if dt_builders is not None:
                    if inc_name is not None:
                        dt_builders = filter(lambda x: x.name == inc_name, dt_builders)  # noqa: F405
                    for bldr in dt_builders:
                        tmp = bldr
                        if isinstance(bldr, LinkBuilder):
                            if inc_spec.linkable:
                                tmp = bldr.builder
                            else:
                                ret.append(IllegalLinkError(self.get_spec_loc(inc_spec),
                                                            location=self.get_builder_loc(tmp)))
                        ret.extend(sub_val.validate(tmp))
                        found = True
            if not found and self.__include_dts[dt].required:
                ret.append(MissingDataType(self.get_spec_loc(self.spec), dt,
                                           location=self.get_builder_loc(builder)))
        it = chain(self.__dataset_validators.items(),
                   self.__group_validators.items())
        for name, validator in it:
            sub_builder = builder.get(name)
            if isinstance(validator, BaseStorageSpec):
                inc_spec = validator
                validator = self.vmap.get_validator(inc_spec)
                def_spec = validator.spec
                if sub_builder is None:
                    if inc_spec.required:
                        ret.append(MissingDataType(self.get_spec_loc(def_spec), def_spec.data_type_def,
                                                   location=self.get_builder_loc(builder)))
                else:
                    ret.extend(validator.validate(sub_builder))

            else:
                spec = validator.spec
                if isinstance(sub_builder, LinkBuilder):
                    if spec.linkable:
                        sub_builder = sub_builder.builder
                    else:
                        ret.append(IllegalLinkError(self.get_spec_loc(spec), location=self.get_builder_loc(builder)))
                        continue
                if sub_builder is None:
                    if spec.required:
                        ret.append(MissingError(self.get_spec_loc(spec), location=self.get_builder_loc(builder)))
                else:
                    ret.extend(validator.validate(sub_builder))

        return ret
