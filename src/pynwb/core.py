import collections as _collections
import itertools as _itertools
import copy as _copy
import abc
from collections import Iterable

import numpy as np

def __type_okay(value, argtype, allow_none=False):
    if value is None:
        return allow_none
    if isinstance(argtype, str):
        if argtype is 'int':
            return __is_int(value)
        elif argtype is 'float':
            return __is_float(value)
        return argtype in [cls.__name__ for cls in value.__class__.__mro__]
    elif isinstance(argtype, type):
        if argtype is int:
            return __is_int(value)
        elif argtype is float:
            return __is_float(value)
        return isinstance(value, argtype)
    elif isinstance(argtype, tuple) or isinstance(argtype, list):
        return any(__type_okay(value, i) for i in argtype)
    elif argtype is None:
        return True
    else:
        raise ValueError("argtype must be a type, a str, a list, a tuple, or None")

def __is_int(value):
    return any(isinstance(value, i) for i in (int, np.int8, np.int16, np.int32, np.int64))

def __is_float(value):
    return any(isinstance(value, i) for i in (float, np.float16, np.float32, np.float64, np.float128))

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
__docval_args_loc = 'args'

# TODO: write unit tests for get_docval* functions
def get_docval(func):
    '''get_docval(func)
    Get a copy of docval arguments for a function
    '''
    func_docval = getattr(func, docval_attr_name, None)
    if func_docval:
        return tuple(func_docval[__docval_args_loc])
    else:
        return tuple()

def get_docval_args(func):
    '''get_docval_args(func)
    Like get_docval, but return only positional arguments
    '''
    func_docval = getattr(func, docval_attr_name, None)
    if func_docval:
        return tuple(a for a in func_docval[__docval_args_loc] if 'default' not in a)
    else:
        return tuple()

def get_docval_kwargs(func):
    '''get_docval_kwargs(func)
    Like get_docval, but return only keyword arguments
    '''
    func_docval = getattr(func, docval_attr_name, None)
    if func_docval:
        return tuple(a for a in func_docval[__docval_args_loc] if 'default' in a)
    else:
        return tuple()

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

    :param enforce_type: Enforce types of input parameters (Default=True)
    :param returns: String describing the return values
    :param rtype: String describing the return the data type of the return values
    :param validator: :py:func:`dict` objects specifying the method parameters
    :param options: additional options for documenting and validating method parameters
    '''
    enforce_type = options.pop('enforce_type', True)
    returns = options.pop('returns', None)
    rtype = options.pop('rtype', None)
    val_copy = __sort_args(_copy.deepcopy(validator))
    def dec(func):
        _docval = _copy.copy(options)
        _docval[__docval_args_loc] = val_copy
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
    '''Generate a Spinxy docstring'''
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
    if len(argnames) < 2:
        raise ValueError('Must supply at least one key and a dict')
    if not isinstance(argnames[-1], dict):
        raise ValueError('last argument must be dict')
    kwargs = argnames[-1]
    if not argnames:
        raise ValueError('must provide keyword to get')
    if len(argnames) == 2:
        return kwargs.get(argnames[0])
    return [kwargs.get(arg) for arg in argnames[:-1]]

def popargs(*argnames):
    '''popargs(*argnames, argdict)
    Convenience function to retrieve and remove arguments from a dictionary in batch
    '''
    if len(argnames) < 2:
        raise ValueError('Must supply at least one key and a dict')
    if not isinstance(argnames[-1], dict):
        raise ValueError('last argument must be dict')
    kwargs = argnames[-1]
    if not argnames:
        raise ValueError('must provide keyword to pop')
    if len(argnames) == 2:
        return kwargs.pop(argnames[0])
    return [kwargs.pop(arg) for arg in argnames[:-1]]

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


class DataChunkIterator(object):
    """Custom iterator class used to iterate over chunks of data.

    Derived classes must ensure that self.shape and self.dtype are set properly.
    define the self.max_shape property describing the maximum shape of the array.
    In addition, derived classes must implement the __next__ method (or overwrite _read_next_chunk
    if the default behavior of __next__ should be reused). The __next__ method must return
    in each iteration 1) a numpy array with the data values for the chunk and 2) a numpy-compliant index tuple
    describing where the chunk is located within the complete data.  HINT: numpy.s_ provides a
    convenient way to generate index tuples using standard array slicing. There are
    a number of additional functions that one can overwrite to customize behavior, e.g,
    the recommended_chunk_size() or recommended_

    The default implementation accepts any iterable and assumes that we iterate over
    the first dimension of the data array. The default implemention supports buffered read,
    i.e., multiple values from the input iterator can be combined to a single chunk. This is
    useful for buffered I/O operations, e.g., to improve performance by accumulating data
    in memory and writing larger blocks at once.
    """
    @docval({'name': 'data', 'type': None, 'doc': 'The data object used for iteration', 'default': None},
            {'name': 'max_shape', 'type': tuple,
             'doc': 'The maximum shape of the full data array. Use None to indicate unlimited dimensions',
             'default': None},
            {'name': 'dtype', 'type': np.dtype, 'doc': 'The Numpy data type for the array', 'default': None},
            {'name': 'buffer_size', 'type': int, 'doc': 'Number of values to be buffered in a chunk', 'default': 1},
            )
    def __init__(self, **kwargs):
        """Initalize the DataChunkIterator"""
        # Get the user parameters
        self.data, self.max_shape, self.dtype, self.buffer_size = getargs('data',
                                                                          'max_shape',
                                                                          'dtype',
                                                                          'buffer_size',
                                                                          kwargs)
        # Create an iterator for the data if possible
        self.__data_iter = iter(self.data) if isinstance(self.data, Iterable) else None
        self.__next_chunk = None
        self.__next_chunk_location = None
        self.__first_chunk_shape = None
        # Determine the shape of the data if possible
        if self.max_shape is None:
            # If the self.data object identifies it shape then use it
            if hasattr(self.data,  "shape"):
                self.max_shape = self.data.shape
                # Avoid the special case of scalar values by making them into a 1D numpy array
                if len(self.max_shape) == 0:
                    self.data = np.asarray([self.data, ])
                    self.max_shape = self.data.shape
                    self.__data_iter = iter(self.data)
            # Try to get an accurate idea of max_shape for other Python datastructures if possible.
            # Don't just call __get_shape for a generator as that would potentially trigger loading of all the data
            elif isinstance(self.data, list) or isinstance(self.data, tuple):
                self.max_shape = self.__get_shape(self.data)

        # If we have a data iterator, then read the first chunk
        if self.__data_iter is not None: # and(self.max_shape is None or self.dtype is None):
            self._read_next_chunk()

        # If we still don't know the shape then try to determine the shape from the first chunk
        if self.max_shape is None and self.__next_chunk is not None:
            data_shape = self.__get_shape(self.__next_chunk)
            self.max_shape = list(data_shape)
            self.max_shape[0] = None
            self.max_shape = tuple(self.max_shape)

        # Determine the type of the data if possible
        if self.__next_chunk is not None:
            self.dtype = self.__next_chunk.dtype
            self.__first_chunk_shape = self.__next_chunk.shape

    def __iter__(self):
        """Return the iterator object"""
        return self

    def _read_next_chunk(self):
        """Read a single chunk from self.__data_iter and store the results in
           self.__next_chunk and self.__chunk_location"""
        if self.__data_iter is not None:
            self.__next_chunk = []
            for i in range(self.buffer_size):
                try:
                    self.__next_chunk.append(next(self.__data_iter))
                except StopIteration:
                    pass
            next_chunk_size = len(self.__next_chunk)
            if next_chunk_size == 0:
                self.__next_chunk = None
                self.__next_chunk_location = None
            else:
                self.__next_chunk = np.asarray(self.__next_chunk)
                if self.__next_chunk_location is None:
                    self.__next_chunk_location = slice(0, next_chunk_size)
                else:
                    self.__next_chunk_location = slice(self.__next_chunk_location.stop,
                                                       self.__next_chunk_location.stop+next_chunk_size)
        else:
            self.__next_chunk = None
            self.__next_chunk_location = None

        return self.__next_chunk, self.__next_chunk_location

    @docval(returns="The following two items must be returned: \n" +
                    "* Numpy array (or scalar) with the data for the next chunk \n" +
                    "* Numpy-compliant index tuple describing the location of the chunk in the complete array. " +
                    "HINT: numpy.s_ provides a convenient way to generate index tuples using standard array slicing.")
    def __next__(self):
        """Return the next data chunk or raise a StopIteration exception if all chunks have been retrieved."""
        # If we have not already read the next chunk, then read it now
        if self.__next_chunk is None:
            self._read_next_chunk()
        # If we do not have any next chunk
        if self.__next_chunk is None:
            raise StopIteration
        # If this is the first time we see a chunk then remember the size of the first chunk
        if self.__first_chunk_shape is None:
            self.__first_chunk_shape = self.__next_chunk.shape
        # Keep the next chunk we need to return
        curr_chunk = self.__next_chunk
        curr_location = self.__next_chunk_location
        # Remove the next chunk from our list since we are returning it here. This avoids having 2 chunks in memory
        self.__next_chunk = None
        # Return the current next chunk
        return curr_chunk, curr_location

    @staticmethod
    def __get_shape(data):
        """Internal helper function used to determin the shape of data objects"""
        def __get_shape_helper(local_data):
            shape = list()
            if hasattr(local_data, '__len__'):
                shape.append(len(local_data))
                if len(local_data) and not isinstance(local_data[0], str):
                    shape.extend(__get_shape_helper(local_data[0]))
            return tuple(shape)
        if hasattr(data, 'shape'):
            return data.shape
        if hasattr(data, '__len__') and not isinstance(data, str):
            return __get_shape_helper(data)
        else:
            return None

    @docval(returns='Tuple with the recommended chunk shape or None if no particular shape is recommended.')
    def recommended_chunk_shape(self):
        """Recommend a chunk shape.

        To optimize iterative write the chunk should be aligned with the common shape of chunks returned by __next__
        or if those chunks are too large, then a well-aligned subset of those chunks. This may also be
        any other value in case one wants to recommend chunk shapes to optimize read rather
        than write. The default implementation returns None, indicating no preferential chunking option."""
        return None

    @docval(returns='Recommended initial shape for the full data. This should be the shape of the full dataset' +
                    'if known beforehand or alternatively the minimum shape of the dataset. Return None if no ' +
                    'recommendation is available')
    def recommended_data_shape(self):
        """Recommend an initial shape of the data. This is useful when progressively writing data and
        we want to recommend and initial size for the dataset"""
        if self.max_shape is not None:
            if np.all([i is not None for i in self.max_shape]):
                return self.max_shape
        return self.__first_chunk_shape