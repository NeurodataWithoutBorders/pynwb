from six import with_metaclass
import numpy as np

from .utils import ExtenderMeta, docval_macro, docval, getargs
from .array import Array


class Query(with_metaclass(ExtenderMeta, object)):

    __operations__ = (
        '__lt__',
        '__gt__',
        '__le__',
        '__ge__',
        '__eq__',
        '__ne__',
    )

    @classmethod
    def __build_operation(cls, op):
        def __func(self, arg):
            return cls(self, op, arg)

    @ExtenderMeta.pre_init
    def __make_operators(cls, name, bases, classdict):
        if not isinstance(cls.__operations__, tuple):
            raise TypeError("'__operations__' must be of type tuple")
        # add any new operations
        if len(bases) and 'Query' in globals() and issubclass(bases[-1], Query) \
           and bases[-1].__operations__ is not cls.__operations__:
                new_operations = list(cls.__operations__)
                new_operations[0:0] = bases[-1].__operations__
                cls.__operations__ = tuple(new_operations)
        for op in cls.__operations__:
            if not hasattr(cls, op):
                setattr(cls, op, cls.__build_operation(op))

    def __init__(self, obj, op, arg):
        self.obj = obj
        self.op = op
        self.arg = arg
        self.collapsed = None
        self.expanded = None

    @docval({'name': 'expand', 'type': bool, 'help': 'whether or not to expand result', 'default': True})
    def evaluate(self, **kwargs):
        expand = getargs('expand', kwargs)
        if expand:
            if self.expanded is None:
                self.expanded = self.__evalhelper()
            return self.expanded
        else:
            if self.collapsed is None:
                self.collapsed = self.__collapse(self.__evalhelper())
            return self.collapsed

    def __evalhelper(self):
        obj = self.obj
        arg = self.arg
        if isinstance(obj, Query):
            obj = obj.evaluate()
        elif isinstance(obj, FORMDataset):
            obj = obj.dataset
        if isinstance(arg, Query):
            arg = self.arg.evaluate()
        return getattr(obj, self.op)(self.arg)

    def __collapse(self, result):
        if isinstance(result, slice):
            return (result.start, result.stop)
        elif isinstance(result, list):
            ret = list()
            for idx in result:
                if isinstance(idx, slice) and (idx.step is None or idx.step == 1):
                    ret.append((idx.start, idx.stop))
                else:
                    ret.append(idx)
            return ret
        else:
            return result

    def __and__(self, other):
        return NotImplemented

    def __or__(self, other):
        return NotImplemented

    def __xor__(self, other):
        return NotImplemented

    def __contains__(self, other):
        return NotImplemented


@docval_macro('data')
class FORMDataset(with_metaclass(ExtenderMeta, object)):

    __operations__ = (
        '__lt__',
        '__gt__',
        '__le__',
        '__ge__',
        '__eq__',
        '__ne__',
    )

    @classmethod
    def __build_operation(cls, op):
        def __func(self, arg):
            return Query(self, op, arg)
        setattr(__func, '__name__', op)
        return __func

    @ExtenderMeta.pre_init
    def __make_operators(cls, name, bases, classdict):
        if not isinstance(cls.__operations__, tuple):
            raise TypeError("'__operations__' must be of type tuple")
        # add any new operations
        if len(bases) and 'Query' in globals() and issubclass(bases[-1], Query) \
           and bases[-1].__operations__ is not cls.__operations__:
                new_operations = list(cls.__operations__)
                new_operations[0:0] = bases[-1].__operations__
                cls.__operations__ = tuple(new_operations)
        for op in cls.__operations__:
            setattr(cls, op, cls.__build_operation(op))

    def __evaluate_key(self, key):
        if isinstance(key, (tuple, list, np.ndarray)):
            return tuple(map(self.__evaluate_key, key))
        else:
            if isinstance(key, Query):
                return key.evaluate()
            return key

    def __getitem__(self, key):
        idx = self.__evaluate_key(key)
        return self.dataset[idx]

    @docval({'name': 'dataset', 'type': ('array_data', Array), 'doc': 'the HDF5 file lazily evaluate'})
    def __init__(self, **kwargs):
        super(FORMDataset, self).__init__()
        self.__dataset = getargs('dataset', kwargs)

    @property
    def dataset(self):
        return self.__dataset

    @property
    def dtype(self):
        return self.__dataset.dtype

    def __len__(self):
        return len(self.__dataset)

    def __iter__(self):
        return iter(self.dataset)

    def __next__(self):
        return next(self.dataset)

    def next(self):
        return self.dataset.next()
