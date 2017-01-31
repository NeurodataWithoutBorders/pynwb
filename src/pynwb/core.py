import collections as _collections
import itertools as _itertools
import copy as _copy
import abc 

def __type_okay(value, argtype, allow_none=False):
    if value is None:
        return allow_none
    if isinstance(argtype, str):
        return argtype in [cls.__name__ for cls in value.__class__.__mro__]
    elif isinstance(argtype, type):
        return isinstance(value, argtype)
    elif isinstance(argtype, tuple) or isinstance(argtype, list):
        return any(__type_okay(value, i) for i in argtype)
    elif argtype is None:
        return True
    else:
        raise ValueError("argtype must be a type, a str, a list, a tuple, or None")

def __format_type(argtype):
    if isinstance(argtype, str):
        return argtype
    elif isinstance(argtype, type):
        return argtype.__name__
    elif isinstance(argtype, tuple) or isinstance(argtype, list):
        types = [__format_type(i) for i in argtype]
        if len(types) > 1:
            return "%s or %s" % (", ".join(types[:-1]), types[-1])
        else:
            return types[0]
    elif argtype is None:
        return "NoneType"
    else:
        raise ValueError("argtype must be a type, str, list, or tuple")

def __parse_args(validator, args, kwargs, enforce_type=True):
    ret = dict()
    errors = list()
    argsi = 0
    for arg in validator:
        argname = arg['name']
        # check if this is a positional argument or not
        #
        # this is a keyword arg
        if 'default' in arg:
            skip_enforce_type = False
            if argname in kwargs:
                ret[argname] = kwargs[argname]
                #skip_enforce_type = ret[argname] is None and arg['default'] is None
            elif len(args) > argsi:
                ret[argname] = args[argsi]
                argsi += 1
            else:
                ret[argname] = arg['default']
                # if default is None, skip the argument check
                # Note: this line effectively only allows NoneType for defaults
                #skip_enforce_type = arg['default'] is None
            if not skip_enforce_type and enforce_type:
                argval = ret[argname]
                if not __type_okay(argval, arg['type'], arg['default'] is None):
                    fmt_val = (argname, type(argval).__name__, __format_type(arg['type']))
                    errors.append("incorrect type for '%s' (got '%s', expected '%s')" % fmt_val)
        # this is a positional arg
        else:
            # check to make sure all positional
            # arguments were passed
            if argsi >= len(args):
                errors.append("missing argument '%s'" % argname) 
            else:
                ret[argname] = args[argsi]
                if enforce_type:
                    argval = ret[argname]
                    if not __type_okay(argval, arg['type']):
                        fmt_val = (argname, type(argval).__name__, __format_type(arg['type']))
                        errors.append("incorrect type for '%s' (got '%s', expected '%s')" % fmt_val)
            argsi += 1
    return {'args': ret, 'errors': errors}

def __sort_args(validator):
    pos = list()
    kw = list()
    for arg in validator:
        if "default" in arg:
            kw.append(arg)
        else:
            pos.append(arg)
    return list(_itertools.chain(pos,kw))

docval_attr_name = 'docval'

#class Arg(object):
#
#    def __init__(self, *args):
#        '''
#        '''
#        self._name = args[0]
#        self._argtype = args[1]
#        self._doc = args[2]
#        if len(args) == 4:
#            self._optional = True
#            self._default = args[3]
#
#    @property
#    def name(self):
#        return self._name
#
#    @property
#    def argtype(self):
#        return self._argtype
#
#    @property
#    def doc(self):
#        return self._doc
#
#    @property
#    def default(self):
#        return self._default
#
#    @property
#    def optional(self):
#        return self._optional
#    

def docval(*validator, **options):
    '''A decorator for documenting and enforcing type for instance method arguments.

    This decorator takes a list of dictionaries that specify the method parameters. These
    dictionaries are used for enforcing type and building a Sphinx docstring. 
    
    The first arguments are dictionaries that specify the positional 
    arguments and keyword arguments of the decorated function. These dictionaries
    must contain the following keys: ``'name'``, ``'type'``, and ``'doc'``. This will define a 
    positional argument. To define a keyword argument, specify a default value
    using the key ``'default'``. 

    The decorated method must take ``self`` and ``**kwargs`` as arguments.

    When using this decorator, the functions :py:func:`~pynwb.core.getargs` and 
    :py:func:`~pynwb.core.popargs` can be used for easily extracting arguments from 
    kwargs.

    The following code example demonstrates the use of this decorator:
    
    .. code-block:: python

       @docval({'name': 'arg1':,   'type': str,           'doc': 'this is the first positional argument'},
               {'name': 'arg2':,   'type': int,           'doc': 'this is the second positional argument'},
               {'name': 'kwarg1':, 'type': (list, tuple), 'doc': 'this is a keyword argument', 'default': list()})
       def foo(self, **kwargs):
           arg1, arg2, kwarg1 = getargs('arg1', 'arg2', 'kwarg1', **kwargs)
           ...

    :param validator: :py:func:`dict` objects specifying the method parameters
    :param options: additional options for documenting and validating method parameters
    '''
    enforce_type = options.pop('enforce_type', True)
    returns = options.pop('returns', None)
    rtype = options.pop('rtype', None)
    val_copy = __sort_args(_copy.deepcopy(validator))
    def dec(func):
        _docval = _copy.copy(options)
        _docval['args'] = val_copy
        def func_call(*args, **kwargs):
            self = args[0]
            parsed = __parse_args(_copy.deepcopy(val_copy), args[1:], kwargs, enforce_type=enforce_type)
            parse_err = parsed.get('errors')
            if parse_err:
                raise TypeError(', '.join(parse_err))
            return func(self, **parsed['args'])
        sphinxy_docstring = __sphinxdoc(func, _docval['args'])
        if returns:
            sphinxy_docstring += "\n:returns: %s" % returns
        if rtype:
            sphinxy_docstring += "\n:rtype: %s" % rtype
        setattr(func_call, '__doc__', sphinxy_docstring)
        setattr(func_call, docval_attr_name, _docval)
        return func_call
    return dec

def __sphinxdoc(func, validator):
    def to_str(argtype):
        if isinstance(argtype, type):
            return argtype.__name__
        return  argtype

    def __sphinx_arg(arg):
        fmt = dict()
        fmt['name'] = arg.get('name')
        fmt['doc'] = arg.get('doc')
        if isinstance(arg['type'], tuple) or isinstance(arg['type'], list):
            fmt['type'] = " or ".join(map(to_str, arg['type']))
        else:
            fmt['type'] = to_str(arg['type'])
        
        tmpl = (":param {name}: {doc}\n"
                ":type  {name}: {type}")
        return tmpl.format(**fmt)

    def __sig_arg(argval):
        if 'default' in argval:
            return "%s=%s" % (argval['name'], str(argval['default']))
        else:
            return argval['name']
    
    sig =  "%s(%s)\n\n" % (func.__name__, ", ".join(map(__sig_arg, validator))) 
    if func.__doc__:
        sig += "%s\n\n" % func.__doc__
    sig += "\n".join(map(__sphinx_arg, validator))
    return sig

def getargs(*argnames):
    '''getargs(*argnames, argdict)
    Convenience function to retrieve arguments from a dictionary in batch
    '''
    if not isinstance(argnames[-1], dict):
        raise ValueError('last argument must be dict')
    kwargs = argnames[-1]
    if not argnames:
        raise ValueError('must provide keyword to get')
    if len(argnames) == 2:
        return kwargs.get(argnames[0])
    return [kwargs.get(arg) for arg in argnames[:-1]]
    #return [ kwargs.get(arg) for arg in argnames ]

def popargs(*argnames):
    '''popargs(*argnames, argdict)
    Convenience function to retrieve and remove arguments from a dictionary in batch
    '''
    if not isinstance(argnames[-1], dict):
        raise ValueError('last argument must be dict')
    kwargs = argnames[-1]
    if not argnames:
        raise ValueError('must provide keyword to pop')
    if len(argnames) == 2:
        return kwargs.pop(argnames[0])
    return [kwargs.get(arg) for arg in argnames[:-1]]


#def properties(*props):
#    """A decorator for automatically setting read-only
#       properties for classes
#    """
#    # we need to use this function to force arg to get
#    # passed into the getter by value
#    def get_getter(arg):
#        argname = "_%s" % arg
#        def _func(self):
#            return getattr(self, argname)
#        return _func
#
#    def outer(cls):
#        classdict = dict(cls.__dict__)
#        for arg in props:
#            getter = get_getter(arg)
#            classdict[arg] = property(getter)
#        return type(cls.__name__, cls.__bases__, classdict)
#    return outer

    
    #@ExtenderMeta.pre_init
    #def print_bases(cls):
    #    print("%s %s" % (cls.__name__, cls.__base__))
    #    base_cls = cls.__base__
    #    for name, func in filter(lambda tup: hasattr(tup[1], docval_attr_name), cls.__dict__.items()):
    #        docval = getattr(func, docval_attr_name)
    #        if hasattr(base_cls, name):
    #            print("base class has %s" % (name))
    #            base_func = getattr(base_cls, name)
    #            if hasattr(base_func, docval_attr_name):
    #                print("%s has docval in base class" % (name))
    #                
    #                base_docval = getattr(base_func, docval_attr_name)
    #                vdict = _collections.OrderedDict()
    #                for arg in base_docval['args']:
    #                    vdict[arg['name']] = arg
    #                for arg in docval['args']:
    #                    vdict[arg['name']] = arg
    #                docval['args'] = list(vdict.values())
    #
    #        def func_call(*args, **kwargs):
    #            self = args[0]
    #            parsed = parse_args(docval['args'], args[1:], kwargs, enforce_type=docval.get('enforce_type', False))
    #            parse_err = parsed.get('errors')
    #            if parse_err:
    #                # TODO: handle parse errors
    #                pass
    #            return func(self, **parsed['args'])
    #        print("%s %s" % (name, docval))
    #        setattr(cls, name, func_call)

class ExtenderMeta(abc.ABCMeta):
    """A metaclass that will extend the base class initialization
       routine by executing additional functions defined in 
       classes that use this metaclass
        
       In general, this class should only be used by core developers.
    """

    __preinit = '__preinit'
    @classmethod
    def pre_init(cls, func):
        setattr(func, cls.__preinit, True)
        return classmethod(func)

    __postinit = '__postinit'
    @classmethod
    def post_init(cls, func):
        '''A decorator for defining a routine to run after creation of a type object.

        An example use of this method would be to define a classmethod that gathers
        any defined methods or attributes after the base Python type construction (i.e. after
        :py:func:`type` has been called)
        '''
        setattr(func, cls.__postinit, True)
        return classmethod(func)

    def __init__(cls, name, bases, classdict):
        it = (getattr(cls, n) for n in dir(cls))
        it = (a for a in it if hasattr(a, cls.__preinit))
        for func in it:
            func(name, bases, classdict)
        super(ExtenderMeta, cls).__init__(name, bases, classdict)
        it = (getattr(cls, n) for n in dir(cls))
        it = (a for a in it if hasattr(a, cls.__postinit))
        for func in it:
            func(name, bases, classdict)

class NWBContainer(metaclass=ExtenderMeta):
    '''The base class to any NWB types.
    
    The purpose of this class is to provide a mechanism for representing hierarchical
    relationships in neurodata.
    '''


    __nwbfields__ = tuple()
    
    @docval({'name': 'parent', 'type': 'NWBContainer', 'doc': 'the parent Container for this Container', 'default': None},
            {'name': 'container_source', 'type': object, 'doc': 'the source of this Container e.g. file name', 'default': None})
    def __init__(self, **kwargs):
        parent, container_source = getargs('parent', 'container_source', kwargs)
        self.__fields = dict()
        self.__subcontainers = list()
        self.__parent = None
        if parent:
            self.parent = parent
        self.__container_source = container_source

    @property
    def container_source(self):
        '''The source of this Container e.g. file name or table
        '''
        return self.__container_source
    
    @property
    def fields(self):
        return self.__fields

    @property
    def subcontainers(self):
        return self.__subcontainers

    @property
    def parent(self):
        '''The parent NWBContainer of this NWBContainer
        '''
        return self.__parent
    
    @parent.setter
    def parent(self, parent_container):
        if self.__parent:
            self.__parent.__subcontainers.remove(self)
        self.__parent = parent_container
        parent_container.__subcontainers.append(self)
  
    @staticmethod
    def __getter(nwbfield):
        def _func(self):
            return self.fields.get(nwbfield)
        return _func
    
    @staticmethod
    def __setter(nwbfield):
        def _func(self, val):
            self.fields[nwbfield] = val
        return _func
    
    @ExtenderMeta.pre_init
    def __gather_nwbfields(cls, name, bases, classdict):
        '''
        This classmethod will be called during class declaration to automatically
        create setters and getters for NWB fields that need to be exported
        '''
        if not isinstance(cls.__nwbfields__, tuple):
            raise TypeError("'__nwbfields__' must be of type tuple")

        if len(bases) and issubclass(bases[-1], NWBContainer) and bases[-1].__nwbfields__ is not cls.__nwbfields__:
                new_nwbfields = list(cls.__nwbfields__)
                new_nwbfields[0:0] = bases[-1].__nwbfields__
                cls.__nwbfields__ = tuple(new_nwbfields)
        for f in cls.__nwbfields__:
            if not hasattr(cls, f):
                setattr(cls, f, property(cls.__getter(f), cls.__setter(f)))

class frozendict(_collections.Mapping):
    '''An immutable dict
    
    This will be useful for getter of dicts that we don't want to support 
    '''
    def __init__(self, somedict):
        self._dict = somedict   # make a copy
        self._hash = None

    def __getitem__(self, key):
        return self._dict[key]

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(frozenset(self._dict.items()))
        return self._hash

    def __eq__(self, other):
        return self._dict == other._dict

    def __contains__(self, key):
        return self._dict.__contains__(key)

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()

