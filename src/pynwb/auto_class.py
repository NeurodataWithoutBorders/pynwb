import re

from pynwb.form.utils import docval
from pynwb import __NS_CATALOG

from pynwb.ecephys import *
from pynwb.icephys import *
from pynwb.file import *
from pynwb.device import *
from pynwb.misc import *
from pynwb.ophys import *
from pynwb.ogen import *
from pynwb.retinotopy import *
from pynwb.behavior import *


def attributes2docval(attributes):
    """
    Takes a spec attribute and creates the appropriate docval entry
    Parameters
    ----------
    attributes: dict

    Returns
    -------
    tuple: docval entry

    """
    args_spec = []

    for attrib in attributes:
        if 'shape' in attrib:
            _type = Iterable
        elif attrib.dtype == 'text':
            _type = str
        else:
            _type = attrib.dtype

        arg_spec = {'name': attrib.name, 'type': _type, 'doc': attrib.doc}
        if 'value' in attrib:
            arg_spec['default'] = attrib.value
        elif not attrib.required:
            arg_spec['default'] = None
        if not attrib.name == 'help':
            args_spec.append(arg_spec)

    return args_spec


def obj2docval(spec):
    """
    Reads spec and automatically generates teh appropriate docval args for the
    constructor.

    Parameters
    ----------
    spec: dict

    Returns
    -------
    tuple for docval

    """

    args_spec = []

    if 'attributes' in spec:
        args_spec += attributes2docval(spec.attributes)

    if 'groups' in spec:
        for group in spec.groups:
            arg_spec = {'name': group.name, 'type': group.neurodata_type_def, 'doc': group.doc}
            if group.quantity in ('?', '*'):
                arg_spec['default'] = None
            args_spec.append(arg_spec)
            args_spec += obj2docval(group)

    if 'datasets' in spec:
        for dataset in spec.datasets:
            arg_spec = {'name': dataset.name, 'type': Iterable, 'doc': dataset.doc}
            if dataset.quantity in ('?', '*'):
                arg_spec['default'] = None
            args_spec.append(arg_spec)
            if 'attributes' in spec:
                args_spec += attributes2docval(dataset.attributes)

    names = [x['name'] for x in args_spec]
    if 'neurodata_type_inc' in spec:
        super_args = eval(spec['neurodata_type_inc']).__init__.__docval__['args']
        for x in super_args:
            if x['name'] not in names:
                args_spec.append(x)

    return tuple(args_spec)


def get_nwbfields(spec):
    """
    Reads spec and determines __nwbfields__ which tells pynwb which attributes
    to write to disk
    Parameters
    ----------
    spec: dict

    Returns
    -------
    tuple of variable names

    """
    vars = [attrib.name for attrib in spec.attributes if attrib.name]
    if hasattr(spec, 'datasets'):
        vars += [dataset.name for dataset in spec.datasets if dataset.name]

    if hasattr(spec, 'groups'):
        for attrib in spec.groups:
            if attrib.name:
                if 'neurodata_type_inc' in attrib or 'neurodata_type_def' in attrib:
                    vars.append({'name': attrib.name, 'child': True})
                else:
                    vars.append(attrib.name)

    return tuple(vars)


def get_class(namespace, data_type, init_pre=lambda **kwargs: None,
              init_post=lambda **kwargs: None):
    """
    Generate class with appropriate constructor for any extension class. Will
    work for all classes, but for MultiContainerInterfaces it is better to use
    auto_class.get_multi_containter().

    Parameters
    ----------
    namespace: str
    data_type: str
    init_pre: func, optional
    init_post: func, optional

    Returns
    -------
    class

    """
    spec = __NS_CATALOG.get_spec(namespace, data_type)
    __nwbfields__ = get_nwbfields(spec)

    @docval(*obj2docval(spec))
    def __init__(self, **kwargs):
        init_pre(**kwargs)
        super_args = [x['name'] for x in super(type(self), self).__init__.__docval__['args']]
        super(type(self), self).__init__(**{arg: kwargs[arg] for arg in super_args
                                            if arg in kwargs and kwargs[arg] is not None})
        for attr, val in kwargs.items():
            try:
                setattr(self, attr, val)
            except AttributeError:
                pass
        init_post(**kwargs)

    d = {'__init__': __init__, '__nwbfields__': __nwbfields__}

    cls = type(spec['neurodata_type_def'], (eval(spec['neurodata_type_inc']),), d)
    register_class(data_type, namespace,  cls)
    return cls


def camel2underscore(name):
    """
    Converts camelcase to underscore e.g. CamelCase -> camel_case
    Parameters
    ----------
    name: str

    Returns
    -------
    str

    """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def psuedo_pluralize(name):
    if not name[-1] == 's':
        return name + 's'
    else:
        return name


def get_multi_container(namespace, data_type, InnerClass):
    """
    Get class for NWBMultiContainerInterface. This is a specific type of class
    that has convenience functions for holding multiple instances of another
    class e.g. a Surgeries class that can hold multiple Surgery objects.

    Parameters
    ----------
    namespace: str
    data_type: str
    InnerClass: class
        Often gotten using `auto_class.get_class()`

    Returns
    -------
    class

    """
    inner_class_name = InnerClass.__name__
    inner_class = camel2underscore(inner_class_name)
    plural_inner_class = psuedo_pluralize(inner_class)

    __clsconf__ = {
        'attr': plural_inner_class,
        'type': InnerClass,
        'add': 'add_' + inner_class,
        'get': 'get_' + inner_class,
        'create': 'create_' + inner_class,
    }

    __help = 'container for ' + plural_inner_class

    d = {'__clsconf__': __clsconf__, '__help': __help}

    cls = type(data_type, (MultiContainerInterface,), d)
    register_class(data_type, namespace, cls)

    return cls
