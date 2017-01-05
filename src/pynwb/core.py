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
    #print("args = %s, kwargs = %s" % (args, kwargs))
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
            #print('parsing %s' % argname)
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

def docval(*validator, **options):
    enforce_type = options.pop('enforce_type', True)
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
        sphinxy_docstring = sphinxdoc(func, _docval['args'])
        setattr(func_call, '__doc__', sphinxy_docstring)
        setattr(func_call, docval_attr_name, _docval)
        return func_call
    return dec

def getargs(*args, **kwargs):
    if len(args) == 1:
        return kwargs.get(args[0])
    return [ kwargs.get(arg) for arg in args ]

def popargs(*args):
    if not isinstance(args[-1], dict):
        raise ValueError('last argument must be dict')
    kwargs = args[-1]
    if not args:
        raise ValueError('must provide keyword to pop')
    if len(args) == 1:
        return kwargs.pop(args[0])
    return [kwargs.get(arg) for arg in args[:-1]]

def huread_doc(func):
    pass

def sphinxdoc(func, validator):
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
    #return "craptastic"

def properties(*props):
    """A decorator for automatically setting read-only
       properties for classes
    """
    # we need to use this function to force arg to get
    # passed into the getter by value
    def get_getter(arg):
        argname = "_%s" % arg
        def _func(self):
            return getattr(self, argname)
        return _func

    def outer(cls):
        classdict = dict(cls.__dict__)
        for arg in props:
            getter = get_getter(arg)
            classdict[arg] = property(getter)
        return type(cls.__name__, cls.__bases__, classdict)
    return outer

    
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
        
       In general, you should not use this class, unless your name is
       Andrew James Tritt.
    """

    #__preinit = '__preinit'
    #@classmethod
    #def pre_init(cls, func):
    #    setattr(func, cls.__preinit, True)
    #    return classmethod(func)

    __postinit = '__postinit'
    @classmethod
    def post_init(cls, func):
        setattr(func, cls.__postinit, True)
        return classmethod(func)

    def __init__(cls, name, bases, classdict):
        #it = (getattr(cls, n) for n in dir(cls))
        #it = (a for a in it if hasattr(a, cls.__preinit))
        #for func in it:
        #    func()
        super(ExtenderMeta, cls).__init__(name, bases, classdict)
        it = (getattr(cls, n) for n in dir(cls))
        it = (a for a in it if hasattr(a, cls.__postinit))
        for func in it:
            func()

