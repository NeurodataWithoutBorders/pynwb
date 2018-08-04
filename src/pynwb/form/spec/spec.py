import abc
from copy import deepcopy
from collections import OrderedDict
import re
from warnings import warn

from ..utils import docval, getargs, popargs, get_docval, fmt_docval_args

NAME_WILDCARD = None
ZERO_OR_ONE = '?'
ZERO_OR_MANY = '*'
ONE_OR_MANY = '+'
DEF_QUANTITY = 1
FLAGS = {
    'zero_or_one': ZERO_OR_ONE,
    'zero_or_many': ZERO_OR_MANY,
    'one_or_many': ONE_OR_MANY
}

from six import with_metaclass  # noqa: E402


class DtypeHelper():
    # Dict where the keys are the primary data type and the values are list of strings with synonyms for the dtype
    primary_dtype_synonyms = {
            'float': ["float", "float32"],
            'double': ["double", "float64"],
            'short': ["int16", "short"],
            'int': ["int32", "int"],
            'long': ["int64", "long"],
            'utf': ["text", "utf", "utf8", "utf-8"],
            'ascii': ["ascii", "bytes"],
            'int8': ["int8"],
            'uint8': ["uint8"],
            'uint16': ["uint16"],
            'uint32': ["uint32", "uint"],
            'uint64': ["uint64"],
            'object': ['object'],
            'region': ['region']
        }

    # List of recommeneded primary dtype strings. These are the keys of primary_dtype_string_synonyms
    recommended_primary_dtypes = list(primary_dtype_synonyms.keys())

    # List of valid primary data type strings
    valid_primary_dtypes = set(list(primary_dtype_synonyms.keys()) +
                               [vi for v in primary_dtype_synonyms.values() for vi in v])

    @staticmethod
    def simplify_cpd_type(cpd_type):
        '''
        Transform a list of DtypeSpecs into a list of strings.
        Use for simple representation of compound type and
        validation.

        :param cpd_type: The list of DtypeSpecs to simplify
        :type cpd_type: list

        '''
        ret = list()
        for exp in cpd_type:
            exp_key = exp.dtype
            if isinstance(exp_key, RefSpec):
                exp_key = exp_key.reftype
            ret.append(exp_key)
        return ret


class ConstructableDict(with_metaclass(abc.ABCMeta, dict)):
    @classmethod
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this ConstructableDict class from a dictionary '''
        return deepcopy(spec_dict)  # noqa: F821

    @classmethod
    def build_spec(cls, spec_dict):
        ''' Build a Spec object from the given Spec dict '''
        vargs = cls.build_const_args(spec_dict)
        args = list()
        kwargs = dict()
        try:

            for x in get_docval(cls.__init__):
                if not x['name'] in vargs:
                    continue
                if 'default' not in x:
                    args.append(vargs.get(x['name']))
                else:
                    kwargs[x['name']] = vargs.get(x['name'])
        except KeyError as e:
            raise KeyError("'%s' not found in %s" % (e.args[0], str(spec_dict)))
        return cls(*args, **kwargs)


class Spec(ConstructableDict):
    ''' A base specification class
    '''

    @docval({'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
            {'name': 'name', 'type': str, 'doc': 'The name of this attribute', 'default': None},
            {'name': 'required', 'type': bool, 'doc': 'whether or not this attribute is required', 'default': True},
            {'name': 'parent', 'type': 'Spec', 'doc': 'the parent of this spec', 'default': None})
    def __init__(self, **kwargs):
        name, doc, required, parent = getargs('name', 'doc', 'required', 'parent', kwargs)
        super(Spec, self).__init__()
        if name is not None:
            self['name'] = name
        if doc is not None:
            self['doc'] = doc
        if not required:
            self['required'] = required
        self._parent = parent

    @property
    def doc(self):
        ''' Documentation on what this Spec is specifying '''
        return self.get('doc', None)

    @property
    def name(self):
        ''' The name of the object being specified '''
        return self.get('name', None)

    @property
    def parent(self):
        ''' The parent specification of this specification '''
        return self._parent

    @parent.setter
    def parent(self, spec):
        ''' Set the parent of this specification '''
        if self._parent is not None:
            raise Exception('Cannot re-assign parent')
        self._parent = spec

    @classmethod
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this Spec class from a dictionary '''
        ret = super(Spec, cls).build_const_args(spec_dict)
        if 'doc' not in ret:
            msg = "'doc' missing: %s" % str(spec_dict)
            raise ValueError(msg)
        return ret

    def __hash__(self):
        return id(self)

#    def __eq__(self, other):
#        return id(self) == id(other)


_target_type_key = 'target_type'

_ref_args = [
    {'name': _target_type_key, 'type': str, 'doc': 'the target type GroupSpec or DatasetSpec'},
    {'name': 'reftype', 'type': str, 'doc': 'the type of references this is i.e. region or object'},
]


class RefSpec(ConstructableDict):

    __allowable_types = ('object', 'region')

    @docval(*_ref_args)
    def __init__(self, **kwargs):
        target_type, reftype = getargs(_target_type_key, 'reftype', kwargs)
        self[_target_type_key] = target_type
        if reftype not in self.__allowable_types:
            msg = "reftype must be one of the following: %s" % ", ".join(self.__allowable_types)
            raise ValueError(msg)
        self['reftype'] = reftype

    @property
    def target_type(self):
        '''The data_type of the target of the reference'''
        return self[_target_type_key]

    @property
    def reftype(self):
        '''The type of reference'''
        return self['reftype']

    @docval(rtype=bool, returns='True if this RefSpec specifies a region reference, False otherwise')
    def is_region(self):
        return self['reftype'] == 'region'


_attr_args = [
        {'name': 'name', 'type': str, 'doc': 'The name of this attribute'},
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'dtype', 'type': (str, RefSpec), 'doc': 'The data type of this attribute'},
        {'name': 'shape', 'type': (list, tuple), 'doc': 'the shape of this dataset', 'default': None},
        {'name': 'dims', 'type': (list, tuple), 'doc': 'the dimensions of this dataset', 'default': None},
        {'name': 'required', 'type': bool,
         'doc': 'whether or not this attribute is required. ignored when "value" is specified', 'default': True},
        {'name': 'parent', 'type': 'BaseStorageSpec', 'doc': 'the parent of this spec', 'default': None},
        {'name': 'value', 'type': None, 'doc': 'a constant value for this attribute', 'default': None},
        {'name': 'default_value', 'type': None, 'doc': 'a default value for this attribute', 'default': None}
]


class AttributeSpec(Spec):
    ''' Specification for attributes
    '''

    @docval(*_attr_args)
    def __init__(self, **kwargs):
        name, dtype, doc, dims, shape, required, parent, value, default_value = getargs(
            'name', 'dtype', 'doc', 'dims', 'shape', 'required', 'parent', 'value', 'default_value', kwargs)
        super(AttributeSpec, self).__init__(doc, name=name, required=required, parent=parent)
        if isinstance(dtype, RefSpec):
            self['dtype'] = dtype
        else:
            self['dtype'] = dtype
            # Validate the dype string
            if self['dtype'] not in DtypeHelper.valid_primary_dtypes:
                raise ValueError('dtype %s not a valid primary data type %s' % (self['dtype'],
                                                                                str(DtypeHelper.valid_primary_dtypes)))
        if value is not None:
            self.pop('required', None)
            self['value'] = value
        if default_value is not None:
            if value is not None:
                raise ValueError("cannot specify 'value' and 'default_value'")
            self['default_value'] = default_value
            self['required'] = False
        if shape is not None:
            self['shape'] = shape
        if dims is not None:
            self['dims'] = dims
            if 'shape' not in self:
                self['shape'] = tuple([None] * len(dims))
        if self.shape is not None and self.dims is not None:
            if len(self['dims']) != len(self['shape']):
                raise ValueError("'dims' and 'shape' must be the same length")

    @property
    def dtype(self):
        ''' The data type of the attribute '''
        return self.get('dtype', None)

    @property
    def value(self):
        ''' The constant value of the attribute. "None" if this attribute is not constant '''
        return self.get('value', None)

    @property
    def default_value(self):
        ''' The default value of the attribute. "None" if this attribute has no default value '''
        return self.get('default_value', None)

    @property
    def required(self):
        ''' True if this attribute is required, False otherwise. '''
        return self.get('required', True)

    @property
    def dims(self):
        ''' The dimensions of this attribute's value '''
        return self.get('dims', None)

    @property
    def shape(self):
        ''' The shape of this attribute's value '''
        return self.get('shape', None)

    @classmethod
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this Spec class from a dictionary '''
        ret = super(AttributeSpec, cls).build_const_args(spec_dict)
        if 'dtype' in ret:
            if isinstance(ret['dtype'], dict):
                ret['dtype'] = RefSpec.build_spec(ret['dtype'])
        return ret


_attrbl_args = [
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'name', 'type': str, 'doc': 'the name of this base storage container', 'default': None},
        {'name': 'default_name', 'type': str,
         'doc': 'The default name of this base storage container', 'default': None},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'quantity', 'type': (str, int), 'doc': 'the required number of allowed instance', 'default': 1},
        {'name': 'data_type_def', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'data_type_inc', 'type': (str, 'BaseStorageSpec'),
         'doc': 'the NWB type this specification extends', 'default': None},
]


class BaseStorageSpec(Spec):
    ''' A specification for any object that can hold attributes. '''

    __inc_key = 'data_type_inc'
    __def_key = 'data_type_def'
    __type_key = 'data_type'

    @docval(*deepcopy(_attrbl_args))  # noqa: F821
    def __init__(self, **kwargs):
        name, doc, parent, quantity, attributes, linkable, data_type_def, data_type_inc =\
             getargs('name', 'doc', 'parent', 'quantity', 'attributes',
                     'linkable', 'data_type_def', 'data_type_inc', kwargs)
        if name == NAME_WILDCARD and data_type_def is None and data_type_inc is None:
            raise ValueError("Cannot create Group or Dataset spec with wildcard name \
            without specifying 'data_type_def' and/or 'data_type_inc'")
        super(BaseStorageSpec, self).__init__(doc, name=name, parent=parent)
        default_name = getargs('default_name', kwargs)
        if default_name:
            if name is not None:
                warn("found 'default_name' with 'name' - ignoring 'default_name'")  # noqa: F821
            else:
                self['default_name'] = default_name
        self.__attributes = dict()
        if quantity in (ONE_OR_MANY, ZERO_OR_MANY):
            if name != NAME_WILDCARD:
                raise ValueError(("Cannot give specific name to something that can ",
                                  "exist multiple times: name='%s', quantity='%s'" % (name, quantity)))
        if quantity != DEF_QUANTITY:
            self['quantity'] = quantity
        if not linkable:
            self['linkable'] = False
        resolve = False
        if data_type_inc is not None:
            if isinstance(data_type_inc, BaseStorageSpec):
                self[self.inc_key()] = data_type_inc.data_type_def
            else:
                self[self.inc_key()] = data_type_inc
        if data_type_def is not None:
            self.pop('required', None)
            self[self.def_key()] = data_type_def
            if data_type_inc is not None and isinstance(data_type_inc, BaseStorageSpec):
                resolve = True
        for attribute in attributes:
            self.set_attribute(attribute)
        self.__new_attributes = set(self.__attributes.keys())
        self.__overridden_attributes = set()
        self.__resolved = False
        if resolve:
            self.resolve_spec(data_type_inc)
            self.__resolved = True

    @property
    def default_name(self):
        '''The default name for this spec'''
        return self.get('default_name', None)

    @property
    def resolved(self):
        return self.__resolved

    @property
    def required(self):
        ''' Whether or not the this spec represents a required field '''
        return self.quantity not in (ZERO_OR_ONE, ZERO_OR_MANY)

    @docval({'name': 'inc_spec', 'type': 'BaseStorageSpec', 'doc': 'the data type this specification represents'})
    def resolve_spec(self, **kwargs):
        inc_spec = getargs('inc_spec', kwargs)
        for attribute in inc_spec.attributes:
            self.__new_attributes.discard(attribute)
            if attribute.name in self.__attributes:
                self.__overridden_attributes.add(attribute.name)
                continue
            self.set_attribute(attribute)

    @docval({'name': 'spec', 'type': (Spec, str), 'doc': 'the specification to check'})
    def is_inherited_spec(self, **kwargs):
        '''
        Return True if this spec was inherited from the parent type, False otherwise
        '''
        spec = getargs('spec', kwargs)
        if isinstance(spec, Spec):
            spec = spec.name
        if spec in self.__attributes:
            return self.is_inherited_attribute(spec)
        return False

    @docval({'name': 'spec', 'type': (Spec, str), 'doc': 'the specification to check'})
    def is_overridden_spec(self, **kwargs):
        '''
        Return True if this spec overrides a specification from the parent type, False otherwise
        '''
        spec = getargs('spec', kwargs)
        if isinstance(spec, Spec):
            spec = spec.name
        if spec in self.__attributes:
            return self.is_overridden_attribute(spec)
        return False

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the attribute to the Spec for'})
    def is_inherited_attribute(self, **kwargs):
        '''
        Return True if the attribute was inherited from the parent type, False otherwise
        '''
        name = getargs('name', kwargs)
        if name not in self.__attributes:
            raise ValueError("Attribute '%s' not found" % name)
        return name not in self.__new_attributes

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the attribute to the Spec for'})
    def is_overridden_attribute(self, **kwargs):
        '''
        Return True if the given attribute overrides the specification from the parent, False otherwise
        '''
        name = getargs('name', kwargs)
        if name not in self.__attributes:
            raise ValueError("Attribute '%s' not found" % name)
        return name not in self.__overridden_attributes

    def is_many(self):
        return self.quantity not in (1, ZERO_OR_ONE)

    @classmethod
    def get_data_type_spec(cls, data_type_def):
        return AttributeSpec(cls.type_key(), 'the data type of this object', 'text', value=data_type_def)

    @classmethod
    def get_namespace_spec(cls):
        return AttributeSpec('namespace', 'the namespace for the data type of this object', 'text', required=False)

    @property
    def attributes(self):
        ''' The attributes for this specification '''
        return tuple(self.get('attributes', tuple()))

    @property
    def linkable(self):
        ''' True if object can be a link, False otherwise '''
        return self.get('linkable', None)

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
    def data_type_inc(self):
        ''' The data type of this specification '''
        return self.get(self.inc_key())

    @property
    def data_type_def(self):
        ''' The data type this specification defines '''
        return self.get(self.def_key(), None)

    @property
    def quantity(self):
        ''' The number of times the object being specified should be present '''
        return self.get('quantity', DEF_QUANTITY)

    @docval(*deepcopy(_attr_args))  # noqa: F821
    def add_attribute(self, **kwargs):
        ''' Add an attribute to this specification '''
        pargs, pkwargs = fmt_docval_args(AttributeSpec.__init__, kwargs)
        spec = AttributeSpec(*pargs, **pkwargs)
        self.set_attribute(spec)
        return spec

    @docval({'name': 'spec', 'type': AttributeSpec, 'doc': 'the specification for the attribute to add'})
    def set_attribute(self, **kwargs):
        ''' Set an attribute on this specification '''
        spec = kwargs.get('spec')
        attributes = self.setdefault('attributes', list())
        if spec.parent is not None:
            spec = AttributeSpec.build_spec(spec)
        if spec.name in self.__attributes:
            idx = -1
            for i, attribute in enumerate(attributes):
                if attribute.name == spec.name:
                    idx = i
                    break
            if idx >= 0:
                attributes[idx] = spec
            else:
                raise ValueError('%s in __attributes but not in spec record' % spec.name)
        else:
            attributes.append(spec)
        self.__attributes[spec.name] = spec
        spec.parent = self

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the attribute to the Spec for'})
    def get_attribute(self, **kwargs):
        ''' Get an attribute on this specification '''
        name = getargs('name', kwargs)
        return self.__attributes.get(name)

    @classmethod
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this Spec class from a dictionary '''
        ret = super(BaseStorageSpec, cls).build_const_args(spec_dict)
        if 'attributes' in ret:
            ret['attributes'] = [AttributeSpec.build_spec(sub_spec) for sub_spec in ret['attributes']]
        return ret


_dt_args = [
    {'name': 'name', 'type': str, 'doc': 'the name of this column'},
    {'name': 'doc', 'type': str, 'doc': 'a description about what this data type is'},
    {'name': 'dtype', 'type': (str, list, RefSpec), 'doc': 'the data type of this column'},
]


class DtypeSpec(ConstructableDict):
    '''A class for specifying a component of a compound type'''

    @docval(*_dt_args)
    def __init__(self, **kwargs):
        doc, name, dtype = getargs('doc', 'name', 'dtype', kwargs)
        self['doc'] = doc
        self['name'] = name
        self.assertValidDtype(dtype)
        self['dtype'] = dtype

    @property
    def doc(self):
        '''Documentation about this component'''
        return self['doc']

    @property
    def name(self):
        '''The name of this component'''
        return self['name']

    @property
    def dtype(self):
        ''' The data type of this component'''
        return self['dtype']

    @staticmethod
    def assertValidDtype(dtype):
        if isinstance(dtype, dict):
            if _target_type_key not in dtype:
                msg = "'dtype' must have the key '%s'" % _target_type_key
                raise AssertionError(msg)
        elif isinstance(dtype, RefSpec):
            pass
        else:
            if dtype not in DtypeHelper.valid_primary_dtypes:
                msg = "'dtype=%s' string not in valid primary data type: %s " % (str(dtype),
                                                                                 str(DtypeHelper.valid_primary_dtypes))
                raise AssertionError(msg)
        return True

    @staticmethod
    @docval({'name': 'spec', 'type': (str, dict), 'doc': 'the spec object to check'}, is_method=False)
    def is_ref(**kwargs):
        spec = getargs('spec', kwargs)
        spec_is_ref = False
        if isinstance(spec, dict):
            if _target_type_key in spec:
                spec_is_ref = True
            elif 'dtype' in spec and isinstance(spec['dtype'], dict) and _target_type_key in spec['dtype']:
                spec_is_ref = True
        return spec_is_ref

    @classmethod
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this Spec class from a dictionary '''
        ret = super(DtypeSpec, cls).build_const_args(spec_dict)
        if isinstance(ret['dtype'], list):
            ret['dtype'] = list(map(cls.build_const_args, ret['dtype']))
        elif isinstance(ret['dtype'], dict):
            ret['dtype'] = RefSpec.build_spec(ret['dtype'])
        return ret


_dataset_args = [
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'dtype', 'type': (str, list, RefSpec),
         'doc': 'The data type of this attribute. Use a list of DtypeSpecs to specify a compound data type.',
         'default': None},
        {'name': 'name', 'type': str, 'doc': 'The name of this dataset', 'default': None},
        {'name': 'default_name', 'type': str, 'doc': 'The default name of this dataset', 'default': None},
        {'name': 'shape', 'type': (list, tuple), 'doc': 'the shape of this dataset', 'default': None},
        {'name': 'dims', 'type': (list, tuple), 'doc': 'the dimensions of this dataset', 'default': None},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'quantity', 'type': (str, int), 'doc': 'the required number of allowed instance', 'default': 1},
        {'name': 'default_value', 'type': None, 'doc': 'a default value for this dataset', 'default': None},
        {'name': 'data_type_def', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'data_type_inc', 'type': (str, 'DatasetSpec'),
         'doc': 'the NWB type this specification extends', 'default': None},
]


class DatasetSpec(BaseStorageSpec):
    ''' Specification for datasets

    To specify a table-like dataset i.e. a compound data type.
    '''

    @docval(*deepcopy(_dataset_args))  # noqa: F821
    def __init__(self, **kwargs):
        doc, shape, dims, dtype, default_value = popargs('doc', 'shape', 'dims', 'dtype', 'default_value', kwargs)
        if shape is not None:
            self['shape'] = shape
        if dims is not None:
            self['dims'] = dims
            if 'shape' not in self:
                self['shape'] = tuple([None] * len(dims))
        if self.shape is not None and self.dims is not None:
            if len(self['dims']) != len(self['shape']):
                raise ValueError("'dims' and 'shape' must be the same length")
        if dtype is not None:
            if isinstance(dtype, list):  # Dtype is a compound data type
                for _i, col in enumerate(dtype):
                    if not isinstance(col, DtypeSpec):
                        msg = 'must use DtypeSpec if defining compound dtype - found %s at element %d' % \
                                (type(col), _i)
                        raise ValueError(msg)
                self['dtype'] = dtype
            elif isinstance(dtype, RefSpec):  # Dtype is a reference
                self['dtype'] = dtype
            else:   # Dtype is a string
                self['dtype'] = dtype
                if self['dtype'] not in DtypeHelper.valid_primary_dtypes:
                    raise ValueError('dtype %s not a valid primary data type %s' %
                                     (self['dtype'], str(DtypeHelper.valid_primary_dtypes)))
        super(DatasetSpec, self).__init__(doc, **kwargs)
        if default_value is not None:
            self['default_value'] = default_value
        if self.name is not None:
            valid_quant_vals = [1, 'zero_or_one', ZERO_OR_ONE]
            if self.quantity not in valid_quant_vals:
                raise ValueError("quantity %s invalid for spec with fixed name. Valid values are: %s" %
                                 (self.quantity, str(valid_quant_vals)))

    @classmethod
    def __get_prec_level(cls, dtype):
        m = re.search('[0-9]+', dtype)
        if m is not None:
            prec = int(m.group())
        else:
            prec = 32
        return (dtype[0], prec)

    @classmethod
    def __is_sub_dtype(cls, orig, new):
        if isinstance(orig, RefSpec):
            if not isinstance(new, RefSpec):
                return False
            return orig == new
        else:
            orig_prec = cls.__get_prec_level(orig)
            new_prec = cls.__get_prec_level(new)
            if orig_prec[0] != new_prec[0]:
                # cannot extend int to float and vice-versa
                return False
            return new_prec >= orig_prec

    @docval({'name': 'inc_spec', 'type': 'DatasetSpec', 'doc': 'the data type this specification represents'})
    def resolve_spec(self, **kwargs):
        inc_spec = getargs('inc_spec', kwargs)
        if isinstance(self.dtype, list):
            # merge the new types
            inc_dtype = inc_spec.dtype
            if isinstance(inc_dtype, str):
                msg = 'Cannot extend simple data type to compound data type'
                raise ValueError(msg)
            order = OrderedDict()
            if inc_dtype is not None:
                for dt in inc_dtype:
                    order[dt['name']] = dt
            for dt in self.dtype:
                name = dt['name']
                if name in order:
                    # verify that the exension has supplied
                    # a valid subtyping of existing type
                    orig = order[name].dtype
                    new = dt.dtype
                    if not self.__is_sub_dtype(orig, new):
                        msg = 'Cannot extend %s to %s' % (str(orig), str(new))
                        raise ValueError(msg)
                order[name] = dt
            self['dtype'] = list(order.values())
        super(DatasetSpec, self).resolve_spec(inc_spec)

    @property
    def dims(self):
        ''' The dimensions of this Dataset '''
        return self.get('dims', None)

    @property
    def dtype(self):
        ''' The data type of the Dataset '''
        return self.get('dtype', None)

    @property
    def shape(self):
        ''' The shape of the dataset '''
        return self.get('shape', None)

    @property
    def default_value(self):
        '''The default value of the dataset or None if not specified'''
        return self.get('default_value', None)

    @classmethod
    def __check_dim(cls, dim, data):
        return True

    @classmethod
    def dtype_spec_cls(cls):
        ''' The class to use when constructing DtypeSpec objects

            Override this if extending to use a class other than DtypeSpec to build
            dataset specifications
        '''
        return DtypeSpec

    @classmethod
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this Spec class from a dictionary '''
        ret = super(DatasetSpec, cls).build_const_args(spec_dict)
        if 'dtype' in ret:
            if isinstance(ret['dtype'], list):
                ret['dtype'] = list(map(cls.dtype_spec_cls().build_spec, ret['dtype']))
            elif isinstance(ret['dtype'], dict):
                ret['dtype'] = RefSpec.build_spec(ret['dtype'])
        return ret


_link_args = [
    {'name': 'doc', 'type': str, 'doc': 'a description about what this link represents'},
    {'name': _target_type_key, 'type': str, 'doc': 'the target type GroupSpec or DatasetSpec'},
    {'name': 'quantity', 'type': (str, int), 'doc': 'the required number of allowed instance', 'default': 1},
    {'name': 'name', 'type': str, 'doc': 'the name of this link', 'default': None}
]


class LinkSpec(Spec):

    @docval(*_link_args)
    def __init__(self, **kwargs):
        doc, target_type, name, quantity = popargs('doc', _target_type_key, 'name', 'quantity', kwargs)
        super(LinkSpec, self).__init__(doc, name, **kwargs)
        self[_target_type_key] = target_type
        if quantity != 1:
            self['quantity'] = quantity

    @property
    def target_type(self):
        ''' The data type of target specification '''
        return self.get(_target_type_key)

    @property
    def data_type_inc(self):
        ''' The data type of target specification '''
        return self.get(_target_type_key)

    def is_many(self):
        return self.quantity not in (1, ZERO_OR_ONE)

    @property
    def quantity(self):
        ''' The number of times the object being specified should be present '''
        return self.get('quantity', DEF_QUANTITY)

    @property
    def required(self):
        ''' Whether or not the this spec represents a required field '''
        return self.quantity not in (ZERO_OR_ONE, ZERO_OR_MANY)


_group_args = [
        {'name': 'doc', 'type': str, 'doc': 'a description about what this specification represents'},
        {'name': 'name', 'type': str, 'doc': 'the name of this group', 'default': None},
        {'name': 'default_name', 'type': str, 'doc': 'The default name of this group', 'default': None},
        {'name': 'groups', 'type': list, 'doc': 'the subgroups in this group', 'default': list()},
        {'name': 'datasets', 'type': list, 'doc': 'the datasets in this group', 'default': list()},
        {'name': 'attributes', 'type': list, 'doc': 'the attributes on this group', 'default': list()},
        {'name': 'links', 'type': list, 'doc': 'the links in this group', 'default': list()},
        {'name': 'linkable', 'type': bool, 'doc': 'whether or not this group can be linked', 'default': True},
        {'name': 'quantity', 'type': (str, int), 'doc': 'the required number of allowed instance', 'default': 1},
        {'name': 'data_type_def', 'type': str, 'doc': 'the NWB type this specification represents', 'default': None},
        {'name': 'data_type_inc', 'type': (str, 'GroupSpec'),
         'doc': 'the NWB type this specification data_type_inc', 'default': None},
]


class GroupSpec(BaseStorageSpec):
    ''' Specification for groups
    '''

    @docval(*deepcopy(_group_args))  # noqa: F821
    def __init__(self, **kwargs):
        doc, groups, datasets, links = popargs('doc', 'groups', 'datasets', 'links', kwargs)
        self.__data_types = dict()
        self.__groups = dict()
        for group in groups:
            self.set_group(group)
        self.__datasets = dict()
        for dataset in datasets:
            self.set_dataset(dataset)
        self.__links = dict()
        for link in links:
            self.set_link(link)
        self.__new_data_types = set(self.__data_types.keys())
        self.__new_datasets = set(self.__datasets.keys())
        self.__overridden_datasets = set()
        self.__new_links = set(self.__links.keys())
        self.__overridden_links = set()
        self.__new_groups = set(self.__groups.keys())
        self.__overridden_groups = set()
        super(GroupSpec, self).__init__(doc, **kwargs)

    @docval({'name': 'inc_spec', 'type': 'GroupSpec', 'doc': 'the data type this specification represents'})
    def resolve_spec(self, **kwargs):
        inc_spec = getargs('inc_spec', kwargs)
        data_types = list()
        # resolve inherited datasets
        for dataset in inc_spec.datasets:
            # if not (dataset.data_type_def is None and dataset.data_type_inc is None):
            if dataset.name is None:
                data_types.append(dataset)
                continue
            self.__new_datasets.discard(dataset.name)
            if dataset.name in self.__datasets:
                self.__datasets[dataset.name].resolve_spec(dataset)
                self.__overridden_datasets.add(dataset.name)
            else:
                self.set_dataset(dataset)
        # resolve inherited groups
        for group in inc_spec.groups:
            # if not (group.data_type_def is None and group.data_type_inc is None):
            if group.name is None:
                data_types.append(group)
                continue
            self.__new_groups.discard(group.name)
            if group.name in self.__groups:
                self.__groups[group.name].resolve_spec(group)
                self.__overridden_groups.add(group.name)
            else:
                self.set_group(group)
        # resolve inherited links
        for link in inc_spec.links:
            if link.data_type_inc is not None:
                data_types.append(link)
            self.__new_links.discard(link.name)
            if link.name in self.__links:
                self.__overridden_links.add(link.name)
                continue
            self.set_link(link)
        # resolve inherited data_types
        for dt_spec in data_types:
            dt = getattr(dt_spec, 'data_type_def',
                         getattr(dt_spec, 'data_type_inc', None))
            self.__new_data_types.discard(dt)
            if dt not in self.__data_types:
                self.__add_data_type_inc(dt_spec)
        super(GroupSpec, self).resolve_spec(inc_spec)

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the dataset'},
            raises="ValueError, if 'name' is not part of this spec")
    def is_inherited_dataset(self, **kwargs):
        '''Return true if a dataset with the given name was inherited'''
        name = getargs('name', kwargs)
        if name not in self.__datasets:
            raise ValueError("Dataset '%s' not found in spec" % name)
        return name not in self.__new_datasets

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the dataset'},
            raises="ValueError, if 'name' is not part of this spec")
    def is_overridden_dataset(self, **kwargs):
        '''Return true if a dataset with the given name overrides a specification from the parent type'''
        name = getargs('name', kwargs)
        if name not in self.__datasets:
            raise ValueError("Dataset '%s' not found in spec" % name)
        return name in self.__overridden_datasets

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the group'},
            raises="ValueError, if 'name' is not part of this spec")
    def is_inherited_group(self, **kwargs):
        '''Return true if a group with the given name was inherited'''
        name = getargs('name', kwargs)
        if name not in self.__groups:
            raise ValueError("Group '%s' not found in spec" % name)
        return name not in self.__new_groups

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the group'},
            raises="ValueError, if 'name' is not part of this spec")
    def is_overridden_group(self, **kwargs):
        '''Return true if a group with the given name overrides a specification from the parent type'''
        name = getargs('name', kwargs)
        if name not in self.__groups:
            raise ValueError("Group '%s' not found in spec" % name)
        return name in self.__overridden_groups

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the link'},
            raises="ValueError, if 'name' is not part of this spec")
    def is_inherited_link(self, **kwargs):
        '''Return true if a link with the given name was inherited'''
        name = getargs('name', kwargs)
        if name not in self.__links:
            raise ValueError("Link '%s' not found in spec" % name)
        return name not in self.__new_links

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the link'},
            raises="ValueError, if 'name' is not part of this spec")
    def is_overridden_link(self, **kwargs):
        '''Return true if a link with the given name overrides a specification from the parent type'''
        name = getargs('name', kwargs)
        if name not in self.__links:
            raise ValueError("Link '%s' not found in spec" % name)
        return name in self.__overridden_links

    @docval({'name': 'spec', 'type': (Spec, str), 'doc': 'the specification to check'})
    def is_inherited_spec(self, **kwargs):
        ''' Returns 'True' if specification was inherited from a parent type '''
        spec = getargs('spec', kwargs)
        if isinstance(spec, Spec):
            name = spec.name
            if name is None:
                name = spec.data_type_def
            if name is None:
                name = spec.data_type_inc
            if name is None:
                raise ValueError('received Spec with wildcard name but no data_type_inc or data_type_def')
            spec = name
        if spec in self.__links:
            return self.is_inherited_link(spec)
        elif spec in self.__groups:
            return self.is_inherited_group(spec)
        elif spec in self.__datasets:
            return self.is_inherited_dataset(spec)
        elif spec in self.__data_types:
            return self.is_inherited_type(spec)
        else:
            if super(GroupSpec, self).is_inherited_spec(spec):
                return True
            else:
                for s in self.__datasets:
                    if self.is_inherited_dataset(s):
                        if self.__datasets[s].get_attribute(spec) is not None:
                            return True
                for s in self.__groups:
                    if self.is_inherited_group(s):
                        if self.__groups[s].get_attribute(spec) is not None:
                            return True
        return False

    @docval({'name': 'spec', 'type': (Spec, str), 'doc': 'the specification to check'})
    def is_overridden_spec(self, **kwargs):
        ''' Returns 'True' if specification was inherited from a parent type '''
        spec = getargs('spec', kwargs)
        if isinstance(spec, Spec):
            name = spec.name
            if name is None:
                name = spec.data_type_def
            if name is None:
                name = spec.data_type_inc
            if name is None:
                raise ValueError('received Spec with wildcard name but no data_type_inc or data_type_def')
            spec = name
        if spec in self.__links:
            return self.is_overridden_link(spec)
        elif spec in self.__groups:
            return self.is_overridden_group(spec)
        elif spec in self.__datasets:
            return self.is_overridden_dataset(spec)
        elif spec in self.__data_types:
            return self.is_overridden_type(spec)
        else:
            if super(GroupSpec, self).is_overridden_spec(spec):  # check if overridden attribute
                return True
            else:
                for s in self.__datasets:
                    if self.is_overridden_dataset(s):
                        if self.__datasets[s].is_overridden_spec(spec):
                            return True
                for s in self.__groups:
                    if self.is_overridden_group(s):
                        if self.__groups[s].is_overridden_spec(spec):
                            return True
        return False

    @docval({'name': 'spec', 'type': (BaseStorageSpec, str), 'doc': 'the specification to check'})
    def is_inherited_type(self, **kwargs):
        ''' Returns True if `spec` represents a spec that was inherited from an included data_type '''
        spec = getargs('spec', kwargs)
        if isinstance(spec, BaseStorageSpec):
            if spec.data_type_def is None:
                raise ValueError('cannot check if something was inherited if it does not have a %s' % self.def_key())
            spec = spec.data_type_def
        # return spec.data_type_def in self.__inherited_data_type_defs
        return spec not in self.__new_data_types

    def __add_data_type_inc(self, spec):
        dt = None
        if hasattr(spec, 'data_type_def') and spec.data_type_def is not None:
            dt = spec.data_type_def
        elif hasattr(spec, 'data_type_inc') and spec.data_type_inc is not None:
            dt = spec.data_type_inc
        if not dt:
            raise TypeError("spec does not have '%s' or '%s' defined" % (self.def_key(), self.inc_key()))
        if dt in self.__data_types:
            curr = self.__data_types[dt]
            if spec.name is None:
                if curr.name is None:
                    raise TypeError('Cannot have multiple data types of the same type without specifying name')
                else:
                    # unnamed data types will be stored as data_types
                    self.__data_types[dt] = spec
            else:
                if curr.name is None:
                    # leave the existing data type as is, since the new one can be retrieved by name
                    return
                else:
                    # store both specific instances of a data type
                    self.__data_types[dt] = [curr, spec]
        else:
            self.__data_types[dt] = spec

    @docval({'name': 'data_type', 'type': str, 'doc': 'the data_type to retrieve'})
    def get_data_type(self, **kwargs):
        '''
        Get a specification by "data_type"
        '''
        ndt = getargs('data_type', kwargs)
        return self.__data_types.get(ndt, None)

    @property
    def groups(self):
        ''' The groups specificed in this GroupSpec '''
        return tuple(self.get('groups', tuple()))

    @property
    def datasets(self):
        ''' The datasets specificed in this GroupSpec '''
        return tuple(self.get('datasets', tuple()))

    @property
    def links(self):
        ''' The links specificed in this GroupSpec '''
        return tuple(self.get('links', tuple()))

    @docval(*deepcopy(_group_args))  # noqa: F821
    def add_group(self, **kwargs):
        ''' Add a new specification for a subgroup to this group specification '''
        doc = kwargs.pop('doc')
        spec = self.__class__(doc, **kwargs)
        self.set_group(spec)
        return spec

    @docval({'name': 'spec', 'type': ('GroupSpec'), 'doc': 'the specification for the subgroup'})
    def set_group(self, **kwargs):
        ''' Add the given specification for a subgroup to this group specification '''
        spec = getargs('spec', kwargs)
        if spec.parent is not None:
            spec = self.build_spec(spec)
        if spec.name == NAME_WILDCARD:
            if spec.data_type_inc is not None or spec.data_type_def is not None:
                self.__add_data_type_inc(spec)
            else:
                raise TypeError("must specify 'name' or 'data_type_inc' in Group spec")
        else:
            if spec.data_type_inc is not None or spec.data_type_def is not None:
                self.__add_data_type_inc(spec)
            self.__groups[spec.name] = spec
        self.setdefault('groups', list()).append(spec)
        spec.parent = self

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the group to the Spec for'})
    def get_group(self, **kwargs):
        ''' Get a specification for a subgroup to this group specification '''
        name = getargs('name', kwargs)
        return self.__groups.get(name, self.__links.get(name))

    @docval(*deepcopy(_dataset_args))  # noqa: F821
    def add_dataset(self, **kwargs):
        ''' Add a new specification for a dataset to this group specification '''
        doc = kwargs.pop('doc')
        spec = self.dataset_spec_cls()(doc, **kwargs)
        self.set_dataset(spec)
        return spec

    @docval({'name': 'spec', 'type': 'DatasetSpec', 'doc': 'the specification for the dataset'})
    def set_dataset(self, **kwargs):
        ''' Add the given specification for a dataset to this group specification '''
        spec = getargs('spec', kwargs)
        if spec.parent is not None:
            spec = self.dataset_spec_cls().build_spec(spec)
        if spec.name == NAME_WILDCARD:
            if spec.data_type_inc is not None or spec.data_type_def is not None:
                self.__add_data_type_inc(spec)
            else:
                raise TypeError("must specify 'name' or 'data_type_inc' in Dataset spec")
        else:
            if spec.data_type_inc is not None or spec.data_type_def is not None:
                self.__add_data_type_inc(spec)
            self.__datasets[spec.name] = spec
        self.setdefault('datasets', list()).append(spec)
        spec.parent = self

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the dataset to the Spec for'})
    def get_dataset(self, **kwargs):
        ''' Get a specification for a dataset to this group specification '''
        name = getargs('name', kwargs)
        return self.__datasets.get(name, self.__links.get(name))

    @docval(*_link_args)
    def add_link(self, **kwargs):
        ''' Add a new specification for a link to this group specification '''
        doc, target_type = popargs('doc', _target_type_key, kwargs)
        spec = self.link_spec_cls()(doc, target_type, **kwargs)
        self.set_link(spec)
        return spec

    @docval({'name': 'spec', 'type': 'LinkSpec', 'doc': 'the specification for the object to link to'})
    def set_link(self, **kwargs):
        ''' Add a given specification for a link to this group specification '''
        spec = getargs('spec', kwargs)
        if spec.parent is not None:
            spec = self.link_spec_cls().build_spec(spec)
        if spec.name == NAME_WILDCARD:
            if spec.data_type_inc is not None or spec.data_type_def is not None:
                self.__add_data_type_inc(spec)
            else:
                raise TypeError("must specify 'name' or 'data_type_inc' in Dataset spec")
        else:
            self.__links[spec.name] = spec
        self.setdefault('links', list()).append(spec)
        spec.parent = self

    @docval({'name': 'name', 'type': str, 'doc': 'the name of the link to the Spec for'})
    def get_link(self, **kwargs):
        ''' Get a specification for a link to this group specification '''
        name = getargs('name', kwargs)
        return self.__links.get(name)

    @classmethod
    def dataset_spec_cls(cls):
        ''' The class to use when constructing DatasetSpec objects

            Override this if extending to use a class other than DatasetSpec to build
            dataset specifications
        '''
        return DatasetSpec

    @classmethod
    def link_spec_cls(cls):
        ''' The class to use when constructing LinkSpec objects

            Override this if extending to use a class other than LinkSpec to build
            link specifications
        '''
        return LinkSpec

    @classmethod
    def build_const_args(cls, spec_dict):
        ''' Build constructor arguments for this Spec class from a dictionary '''
        ret = super(GroupSpec, cls).build_const_args(spec_dict)
        if 'datasets' in ret:
            ret['datasets'] = list(map(cls.dataset_spec_cls().build_spec, ret['datasets']))
        if 'groups' in ret:
            ret['groups'] = list(map(cls.build_spec, ret['groups']))
        if 'links' in ret:
            ret['links'] = list(map(cls.link_spec_cls().build_spec, ret['links']))
        return ret
