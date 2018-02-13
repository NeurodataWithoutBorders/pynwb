from six import with_metaclass
from abc import abstractmethod
import numpy as np
import math

from .utils import ExtenderMeta, docval_macro


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
        self.result = None

    def evaluate(self):
        if self.result is None:
            obj = self.obj
            if isinstance(obj, Query):
                obj = obj.evaluate()
            elif isinstance(obj, FORMDataset):
                obj = obj.get_array()
            self.result = getattr(obj, self.op)(self.arg)
        return self.result

    def __and__(self, other):
        pass

    def __or__(self, other):
        pass

    def __xor__(self, other):
        pass

    def __contains__(self, other):
        pass


@docval_macro('data')
class FORMDataset(with_metaclass(ExtenderMeta, object)):

    __operations__ = (
        '__lt__',
        '__gt__',
        '__le__',
        '__ge__',
        '__eq__',
        '__ne__',
        '__len__',
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
        return self.get_array()[idx]

    def __init__(self, h5_dataset):
        self.data = h5_dataset

    def get_array(self):
        return self.data


class AbstractSortedDataset(object):

    @abstractmethod
    def find_point(self, val):
        pass

    def __lower(self, other):
        ins = self.find_point(other)
        return ins

    def __upper(self, other):
        ins = self.__lower(other)
        while self[ins] == other:
            ins += 1
        return ins

    def __lt__(self, other):
        ins = self.__lower(other)
        return slice(0, ins)

    def __le__(self, other):
        ins = self.__upper(other)
        return slice(0, ins)

    def __gt__(self, other):
        ins = self.__upper(other)
        return slice(ins, len(self))

    def __ge__(self, other):
        ins = self.__lower(other)
        return slice(ins, len(self))

    @staticmethod
    def __sort(self, a):
        if isinstance(a, tuple):
            return a[0]
        else:
            return a

    def __eq__(self, other):
        if isinstance(other, list):
            ret = list()
            for i in other:
                eq = self == i
                ret.append(eq)
            # TODO: sort this and collapse
            ret = sorted(ret, key=self.__sort)
            tmp = list()
            for i in range(1, len(ret)):
                a, b = ret[i-1], ret[i]
                if isinstance(a, tuple):
                    if isinstance(b, tuple):
                        if a[1] >= b[0]:
                            b[0] = a[0]
                        else:
                            tmp.append(slice(*a))
                    else:
                        if b > a[1]:
                            tmp.append(slice(*a))
                        elif b == a[1]:
                            a[1] == b+1
                        else:
                            ret[i] = a
                else:
                    if isinstance(b, tuple):
                        if a < b[0]:
                            tmp.append(a)
                    else:
                        if b - a == 1:
                            ret[i] = (a, b)
                        else:
                            tmp.append(a)
            if isinstance(ret[-1], tuple):
                tmp.append(slice(*ret[-1]))
            else:
                tmp.append(ret[-1])
            ret = tmp
            return ret
        elif isinstance(other, tuple):
            ge = self >= other
            ge = ge[0]
            lt = self < other
            lt = lt[1]
            if ge == lt:
                return ge
            else:
                return (ge, lt)
        else:
            lower = self.__lower(other)
            upper = self.__upper(other)
            d = upper - lower
            if d == 1:
                return lower
            elif d == 0:
                return None
            else:
                return (lower, upper)

    def __ne__(self, other):
        eq = self == other
        if isinstance(eq, tuple):
            return [slice(0, eq[0]), slice(eq[1], len(self))]
        else:
            return [slice(0, eq), slice(eq+1, len(self))]


class SortedDataset(AbstractSortedDataset):

    def __init__(self, array):
        self.array = array

    def get_array(self):
        return self.array

    def find_point(self, val):
        return np.searchsorted(self.get_array(), val)

    def __getitem__(self, arg):
        return self.array.__getitem__(arg)

    def __len__(self):
        return len(self.array)


class LinSpace(SortedDataset):

    def __init__(self, start, stop, step):
        self.start = start
        self.stop = stop
        self.step = step
        self.__len = int((stop - start)/step)

    def __len__(self):
        return self.__len

    def find_point(self, val):
        nsteps = (val-self.start)/self.step
        fl = math.floor(nsteps)
        if fl == nsteps:
            return int(fl)
        else:
            return int(fl+1)

    def __calcidx(self, arg):
        return self.start + self.step*arg

    def __gendata(self, arg):
        for i in arg:
            if isinstance(i, slice):
                for j in map(self.__calcidx, range(i.start, i.stop, 1)):
                    yield j
            elif isinstance(i, int):
                yield self.__calcidx(i)

    def __getitem__(self, arg):
        if isinstance(arg, int):
            return self.__calcidx(arg)
        else:
            tmp = arg
            if isinstance(tmp, slice):
                tmp = [tmp]
            return list(self.__gendata(tmp))
