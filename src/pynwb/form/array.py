import numpy as np
from abc import abstractmethod, ABCMeta
from six import with_metaclass
from math import ceil, floor


class Array(object):

    def __init__(self, data, dtype=None):
        self.__data = data
        if dtype is not None:
            self.dtype = dtype
        elif hasattr(data, 'dtype'):
            self.dtype = data.dtype
        else:
            tmp = data
            while isinstance(tmp, (list, tuple)):
                if len(tmp) > 0:
                    tmp = tmp[0]
                else:
                    raise ValueError("Cannot determine dtype for empty array")
            self.dtype = type(tmp)

    @property
    def data(self):
        return self.__data

    def __len__(self):
        return len(self.__data)

    def get_data(self):
        return self.__data

    def __getidx__(self, arg):

        return self.__data[arg]

    def __sliceiter(self, arg):
        return (x for x in range(*arg.indices(len(self))))

    def __getitem__(self, arg):
        if isinstance(arg, list):
            idx = list()
            for i in arg:
                if isinstance(i, slice):
                    idx.extend(x for x in self.__sliceiter(i))
                else:
                    idx.append(i)
            return np.fromiter((self.__getidx__(x) for x in idx), dtype=self.dtype)
        elif isinstance(arg, slice):
            return np.fromiter((self.__getidx__(x) for x in self.__sliceiter(arg)), dtype=self.dtype)
        elif isinstance(arg, tuple):
            return (self.__getidx__(arg[0]), self.__getidx__(arg[1]))
        else:
            return self.__getidx__(arg)


class AbstractSortedArray(with_metaclass(ABCMeta, Array)):
    '''
    An abstract class for representing sorted array
    '''

    @abstractmethod
    def find_point(self, val, side):
        pass

    def get_data(self):
        return self

    def __lower(self, other):
        ins = self.find_point(other, 'left')
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
    def __sort(a):
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
            ge = self >= other[0]
            ge = ge.start
            lt = self < other[1]
            lt = lt.stop
            if ge == lt:
                return ge
            else:
                return slice(ge, lt)
        else:
            lower = self.__lower(other)
            upper = self.__upper(other)
            d = upper - lower
            if d == 1:
                return lower
            elif d == 0:
                return None
            else:
                return slice(lower, upper)

    def __ne__(self, other):
        eq = self == other
        if isinstance(eq, tuple):
            return [slice(0, eq[0]), slice(eq[1], len(self))]
        else:
            return [slice(0, eq), slice(eq+1, len(self))]


class SortedArray(AbstractSortedArray):
    '''
    A class for wrapping sorted arrays. This class overrides
    <,>,<=,>=,==, and != to leverage the sorted content for
    efficiency.
    '''

    def __init__(self, array, dtype=None):
        super(SortedArray, self).__init__(array)
        if dtype is not None:
            self.dtype = dtype

    def find_point(self, val, side='left'):
        return np.searchsorted(self.data, val, side=side)


class LinSpace(SortedArray):

    def __init__(self, start, stop, step):
        self.start = start
        self.stop = stop
        self.step = step
        self.dtype = np.asarray(start).dtype
        self.__len = int((stop - start)/step)
        self.__current_iter_step = -1

    def __len__(self):
        return self.__len

    def __iter__(self):
        return self

    def __next__(self):
        self.__current_iter_step += 1
        if self.__current_iter_step < len(self):
            return self[self.__current_iter_step]
        else:
            self.__current_iter_step = -1
            raise StopIteration

    def find_point(self, val, side):
        nsteps = (val - self.start) / self.step
        if nsteps < 0 or val > self.stop:
            raise ValueError("%s out of range")
        if side == 'left':
            fl = int(floor(nsteps))
        elif side == 'right':
            fl = int(ceil(nsteps))
        return fl

    def __getidx__(self, arg):
        loc = arg if arg >= 0 else len(self) + arg
        val = self.start + self.step * loc
        if val < self.start or val > self.stop:
            raise IndexError("Value out of range")
        return val

    @property
    def shape(self):
        return (len(self), )
