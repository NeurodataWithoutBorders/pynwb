'''This submodule will contain classes and objects for validating
the NWB format schema.
'''

# A dictionary for storing the format schema
# We will initialize this in __init__
__schema__ = {}

class ImmutableGroup(h5py.Group):
    def __setitem__(self, args, val):
        raise NotImplementedError('__setitem__')

class ImmutableDataset(h5py.Dataset):
    def __setitem__(self, args, val):
        raise NotImplementedError('__setitem__')

def h5_scalar(func):
    def inner():
        return func().value
    return inner

def get_timeseries_name(group):
    return group.name.split('/')[-1]

def __is_timeseries__(group):
    return 'ancestry' in group.attrs

def find_timeseries(f):
    def __find_timeseries__(d, group):
        if __is_timeseries__(group):
            d[get_timeseries_name(group)] = group
        else:
            for key in group.keys():
                if isinstance(group[key], h5py.Group):
                    __find_timeseries__(d,group[key])
    ret = dict()
    find_timeseries(ret, f)
    return ret
    
    
class NWBFile(ImmutableGroup, h5py.File):
    '''This class serves as a wrapper for an h5py.File object
    that enforces NWB specifications at the top-level. For, example
    this is where we enforce the existence of the group "general"
    '''
    def __init__(self, path):
        """Open a new NWBFile for reading

        :param path: The path to the NWB file to open
        :type path: str.
        :raises: NwbParseError
        """
        super(filename, 'r')
        # TODO: This is just a placeholder to convey what we want to do here
        # When validation code is established, the actual function name and use
        # needs to be added
        if not _schema.validate_nwb(self):
            raise NWBSyntaxError()
        self._create_date = [datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S") for date_str in self['file_create_date']]
        self._start_time = datetime.strptime(self['session_start_time'], "%Y-%m-%dT%H:%M:%S")
         
        self._timeseries = find_timeseris(self)
        # TODO: Do some stuff to add all the TimeSeries datasets
        # for easy access
            

        
    @property
    @h5_scalar
    def nwb_version(self):
        """The NWB version for this file
        """
        return self['nwb_version']

    @property
    def modification_dates(self):
        """The modification dates of this file. The 0-element will be the file creation date.
        """
        return self._create_date

    @property
    @h5_scalar
    def description(self):
        """A description of the experiment and data in this file
        """
        return self['session_description']

    @property
    @h5_scalar
    def identifier(self):
        """The identifier for this NWB file
        """
        return self['identifier']

    @property
    def start_time(self):
        """A description of the experiment and data in this file
        """
        return self._start_time
    
    def get_timeseries(self, name):
        '''Return the TimeSeries objects corresponding to the given name
        
        
        '''
        return self._timeseries[name]
    
    def close(self):
        '''Validate that this HDF5 file is a valid NWB file, and then close'''
        super().close()
    

