import numpy as np
from collections import Iterable
from pynwb.form.utils import docval, popargs, fmt_docval_args

# not sure if I need to register_class DataIO

class DataIO:

    @docval({'name': 'data', 'type': (list, np.ndarray, Iterable), 'doc': 'the data to be written'},
            {'name': 'compress', 'type': bool, 'doc': 'Flag to use gzip compression filter on dataset', 'default': False}
            )
    def __init__(self, **kwargs):
        data, compress = popargs('data', 'compress', kwargs)
        self.__data = data
        self.__compress = compress

    @property
    def data(self):
        return self.__data

    @property
    def compress(self):
        return self.__compress
