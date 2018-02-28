import numpy as np
from abc import abstractmethod, ABCMeta
from six import with_metaclass


class Array(object):

    def __init__(self, data):
        self.__data = data
        if hasattr(data, 'dtype'):
            self.dtype = data.dtype
        else:
            tmp = data
            while isinstance(tmp, (list, tuple)):
                tmp = tmp[0]
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
    def find_point(self, val):
        pass

    def get_data(self):
        return self

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

    def __init__(self, array):
        super(SortedArray, self).__init__(array)

    def find_point(self, val):
        return np.searchsorted(self.data, val)


class LinSpace(SortedArray):

    def __init__(self, start, stop, step):
        self.start = start
        self.stop = stop
        self.step = step
        self.dtype = float if any(isinstance(s, float) for s in (start, stop, step)) else int
        self.__len = int((stop - start)/step)

    def __len__(self):
        return self.__len

    def find_point(self, val):
        nsteps = (val-self.start)/self.step
        fl = int(nsteps)
        if fl == nsteps:
            return int(fl)
        else:
            return int(fl+1)

    def __getidx__(self, arg):
        return self.start + self.step*arg
