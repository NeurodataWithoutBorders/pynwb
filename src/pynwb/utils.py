from itertools import chain as __chain
import copy as __copy


def __type_okay(value, argtype):
    return True

def __parse_args(validator, args, kwargs, enforce_type=True):
    ret = dict()
    errors = list()
    argi = 0
    for arg in validator:
        argname = arg['name']
        # check if this is a positional argument or not
        if 'default' in arg:
            # this is a key-value arg
            if argname in kwargs:
                ret[argname] = kwargs[argname]
            elif len(args) > argi:
                ret[argname] = args[argi]
                argi += 1
            else:
                ret[argname] = arg['default']
        else:
            # this is a positional arg
            ret[argname] = args[argi]
            argi += 1
        if not __type_okay(ret[argname], arg['type']):
            errors.append(argname)
    
    return {'args': ret, 'errors': errors}

def __check_redundant():
    pass


def __sort_args(validator):
    pos = list()
    kw = list()
    for arg in validator:
        if "default" in arg:
            kw.append(arg)
        else:
            pos.append(arg)
    return list(__chain(pos,kw))

def docstring(func):
    def __sphinx_args(validator):
        tmp = copy.copy(validator)
        if isinstance(tmp['type'], type):
            tmp['type'] = tmp['type'].__name__
        tmpl = (":param {name}: {doc}\n"
                ":type  {name}: {type}")
    return tmpl.format(**validator)
    
    if hasattr(func, 'validator'):
        validator = func.validator
    else:
        return None
    pos = list()
    kw = list()
    sig =  ".. py:function:: %s(%s)\n\n" % (func.__name__, ", ".join(x['name'] for x in validator)) 
    sig += "%s\n\n" % func.__doc__
    sig += "\n".join(map(__sphinx_args, func.docval['args']))

def docval(*validator, **options):
    docval_attr_name = 'docval'
    enforce_type = options.pop('enforce_type', False)
    validator = __sort_args(validator)
    def dec(func):
        _docval = __copy.copy(options)
        _docval['args'] = validator
        def func_call(*args, **kwargs):
            self = args[0]
            parsed = __parse_args(validator, args[1:], kwargs, enforce_type=enforce_type)
            parse_err = parsed.get('errors')
            if parse_err:
                # TODO: handle parse errors
                pass
            return func(self, **parsed['args'])
        setattr(func_call, docval_attr_name, _docval)
        return func_call
    return dec

def getargs(*args, **kwargs):
    for arg in args:
        yield kwargs[args]

# LEAVING THIS HERE IN CASE WE WANT TO TRY TO RESURRECT
#
#def __merge_args(base_validator, validator):
#    vdict = OrderedDict()
#    for arg in base_validator:
#        vdict[arg['name']] = arg
#    for arg in validator:
#        vdict[arg['name']] = arg
#    return __sort_args(list(vdict.values()))
#     inherit_args = options.pop('inherit_args', False)
#         if inherit_args:
#             print('------------- inheriting args')
#             parcl = func.__class__.__base__
#             print('function belongs to %s' % func.__class__)
#             print('base class is %s' % parcl)
#             if hasattr(parcl, func.__name__):
#                 print('------------- parent has function')
#                 parmeth = getattr(parcl, func.__name__)
#                 if hasattr(parmeth, docval_attr_name):
#                     print('------------- function has docval')
#                     _docval['args'] = __merge_args(getattr(parmeth, docval_attr_name), validator)
