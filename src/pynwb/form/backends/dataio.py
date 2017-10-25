import numpy as np
from collections import Iterable
from form.utils import docval, popargs, fmt_docval_args

# not sure if I need to register_class DataIO

class DataIO:
    @docval({'name': 'data', 'type': (list, np.ndarray, Iterable), 'doc': 'The data to be set in the datawrapper. Can be experiment data or timestamps. Can also store binary data e.g. image frames'},
            {'name': 'compress', 'type': bool, 'doc': 'Flag to use gzip compression filter on dataset'}            
            )
    def __init__(self, **kwargs):
        data, compress = popargs('data', 'compress', kwargs)
        self.data = data
        self.compress = compress

    def getdata(self):
        return(self.data)

    def getcompress(self):
        return(self.compress)
