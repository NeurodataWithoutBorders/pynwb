
def get_timeseries(schema):
    '''Returns an iterable over TimeSeries type specifications
    '''
    pass


class TimeSeriesValidator(object):
    
    def __init__(self, name, groups, datasets, attributes):
        self.name = name
        self.groups = groups
        self.datasets = datasets
        self.attributes = attributes

    def validate(self, group):
        '''Inspect the HDF5 Group to determine if it 
        conforms to the specifications defined in this TimeSeriesValidator
        '''
        pass
