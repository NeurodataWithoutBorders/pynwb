'''This submodule will contain classes and objects for validating
the NWB format schema.
'''

from .h5tools import h5_scalar, sync_files
from .nwbtools import find_timeseries 

# A dictionary for storing the format schema
# We will initialize this in __init__
__schema__ = {}
    
#class NeurodataFile(ImmutableGroup, h5py.File):
class NeurodataFile(h5py.File):
    """This class serves as a wrapper for an h5py.File object
    that enforces NWB specifications at the top-level. For, example
    this is where we enforce the existence of the group "general"
    """
    
    def __init__(self, path, mode='r', master=None):
        """Open a new NWBFile for reading

        :param path: The path to the NWB file to open
        :type path: str.
        :param mode: The mode to open the file in
        :type path: str.
        :param master: The master file to create a subfile to. Use this for 
                       'appending' to existing files. This is useful for 
                       adding analysis results to raw data files
        :type master: NeurodataFile.


        :raises: NWBParseError
        """

        super(filename, mode)
        if master:
            master.add_data_file(self)
        # TODO: This is just a placeholder to convey what we want to do here
        # When validation code is established, the actual function name and use
        # needs to be added
        if not _schema.validate_nwb(self):
            raise NWBSyntaxError()
        self._create_date = [datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S") for date_str in self['file_create_date']]
        self._start_time = datetime.strptime(self['session_start_time'], "%Y-%m-%dT%H:%M:%S")
        self._timeseries = dict()
        

    def add_data_file(self, child):
        """Connect child to self via appropriate links. 
        Use this to add a new file to a collection of NWB files 
        """
        sync_files(self, child)
        


    def add_timeseries(self, timeseries):
        pass


    def create_raw_timeseries(*args, **kwargs):
        """
            timeseries_type, comments, attributes
        """
        ts_type = args[0]
        name = args[1]
        data = args[2]
        comments = args[3]
        validator = getattr(nwbtools.validators, ts_type)
        object_specs = list()
        attributes = dict()
        # do some stuff to build the dict needed for writing with h5tools.write_group
        group = self.create_group(name)
        missing_specs = validator.validate(object_specs, attributes)
        if not len(missing_specs):
            h5tools.write_group(group, object_specs, attributes)

    def create_analysis_result(*args, **kwargs):
        pass
        
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
    
    def fetch_timeseries(self, *args, **kwargs):
        '''Return the TimeSeries objects corresponding to the given name
        
        :param name: the name of the 
        
        '''
        if name in self._timeseries:
            if len(self._timeseries[name]):
            return self._timeseries[name]
        else:
            result = self.visit
            
            #
            return None
    
    def close(self):
        '''Validate that this HDF5 file is a valid NWB file, and then close'''
        super().close()

class TimeSeries(ImmutableGroup):

    def __init__(self, ):
        pass
    
    @property
    @h5_scalar
    def comments(self):
        return self['comments']
    
    
for prop in ('comments', 'description', 'help', 'source'):
    setattr(TimeSeries, prop, property(h5_scalar(lambda self: self[prop])))
    


    
