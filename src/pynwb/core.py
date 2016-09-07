'''This submodule will contain classes and objects for validating
the NWB format schema.
'''

# A dictionary for storing the format schema
# We will initialize this in __init__
__schema__ = {}

class AbstractNWBDataFactory(object):
    def __init__(self):
        pass

class TimeSeriesFactory(AbstractNWBDataFactory):
    '''This class will be used to enforce specifications for
    TimeSeries types specified in NWB
    '''
    def __init__(self, spec):
        self.spec = spec
        pass

    def build(self, group, attributes):
        '''This will use spec to extract the necessary data
        from attributes and set them as HDF5 attributes
        
        It will also determine if the timestamps dataset will be present (i.e check for 'starting_time')
        
        Returns:
            (data, timestamp): data will be the h5py.Dataset
        
        Raises:
            MissingAttributesError: if attributes is missing required attributes
        '''
        pass

    def get_missing_attributes(self, attributes):
        '''Returns the attributes that are missing from the given dictionary
        '''
        pass


class NWBFile(ImmutableGroup, h5py.File):
    '''This class serves as a wrapper for an h5py.File object
    that enforces NWB specifications at the top-level. For, example
    this is where we enforce the existence of the group "general"
    '''
    def __init__(self):
        pass
    
    def get_group(self, name):
        '''Return the h5py.Group corresponding to the given name
        
        Args:
            name: the name of the Group object to return
        '''
        pass
    
    def close(self):
        '''Validate that this HDF5 file is a valid NWB file, and then close'''
        super().close()
    

    def __setitem__(self, args, val):
        raise NotImplementedError('__setitem__')
    

class ImmutableGroup(h5py.Group):
    def __setitem__(self, args, val):
        raise NotImplementedError('__setitem__')

class ImmutableDataset(h5py.Dataset):
    def __setitem__(self, args, val):
        raise NotImplementedError('__setitem__')

