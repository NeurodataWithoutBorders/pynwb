'''This ackage will contain functions, classes, and objects
for reading and writing data in NWB format
'''
import data

def open(*args, **kwargs):
    '''Use this to open a NWB File
    Args:
        path: path to the NWB File to open
        mode: the mode to open the file in. supported modes are 
                * r          Readonly, file must exist
                * r+         Read/write, file must exist
                * w          Create file, truncate if exists
                * w- or x    Create file, fail if exists
                * a          Read/write if exists, create otherwise (default)
    Returns:
        An NWBFile object

    '''
    from data import NWBFile 
    path = args[0]
    mode = args[1]
    f = _h5py.File(path, mode)
    return NWBFile(f)


def create_timeseries(*args, **kwargs):
    '''Add a TimeSeries dataset to an NWB File
    '''
    nwb_file = args[0]
    timeseries_type = args[1]
    ts_name = args[2]
    shape = args[3]
    data = args[4]
    
    try:
        validator = getattr(data, timeseries_type)
    except AttributeError as ae:
        raise UndefinedTimeSeriesError(timeseries_type)
    
    missing_attributes = validator.get_missing_attributes(kwargs):
    if not len(missing_attributes):
        raise MissingAttributesError(missing_attributes)

    # an h5py.Group
    group = nwb_file.get_group(validator.location)

    (data, timestamps) = validator.build(group, kwargs)
        
    if timestamps:
        ''' 
        do some stuff to handle populating the timestamps 'dataset'
        in addition to the 'data' dataset
        ''' 
        pass
    else:
        ''' 
        do some stuff to populate the 'data' dataset
        ''' 
        pass
