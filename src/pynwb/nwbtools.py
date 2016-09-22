
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


class TimeSeriesValidator(object):
    def __init__(self, spec):
        pass
    
class AttributeValidator(object):
    def __init__(self, spec):
        self.data_type = spec['data_type']
        if 'dimensions' in spec:
            self.dimensions = spec['dimensions']
        else:
            self.dimensions = ()
    
    def validate(self, spec):
        reasons = list()
        if get_shape(spec['value']) != self.dimensions:
            #TODO This will probably need to be more sophisticated
            
            reasons.append('incorrect shape')
        if not isinstance(get_value(spec['value']), self.data_type)
            reasons.append('incorrect data type')
            
        return tuple(reasons)
        

class AttributesValidator(object):
    def __init__(self, attributes):
        for attr, spec in attributes.iteritems():
            self.required_attributes = AttributeValidator(spec)
        
    def validate(self, attributes):
        reasons = list()
        for attr in self.required_attributes.keys():
            if attr in attributes:
                # do something to check type
                pass 
            else:
                reasons.append((attr, "missing required attribute %s" % attr))

class GroupValidator(AttributesValidator):
    def __init__(self, attributes, datasets, groups):
        super().__init__(self, kwargs['attributes'])
        self.required_datasets = required_datasets
        for dset_name, spec in kwargs['datasets']:
            self.required_datasets[dset_name] = DatasetValidator(datasets)
        for grp_name, spec in kwargs['groups']:
            self.required_groups[grp_name] = GroupValidator(groups)
    
    def validate(self, attributes, datasets, groups):
        reasons = super().validate(attributes)
        for grp_name, grp_validator in self.required_groups.iteritems():
            if grp_name in groups:
                grp_validator.validate(groups[grp_name])
            else:
                reasons.append("missing required group '%'" % grp_name)
        for dset_name, dset_validator in self.required_datasets.iteritems():
            if dset_name in datasets:
                dset_validator.validate(datasets[dset_name])
            else:
                reasons.append("missing required group '%'" % grp_name)
        
            
        return tuple(reasons)

class DatasetValidator(AttributesValidator):
    def __init__(self, data_type, dimensions, required_attributes):
        super().__init__(self, attributes)
        self.data_type = data_type
        self.dimensions = dimensions

    def validate(self, attributes, data):
        reasons = super().validate(attributes)
        if get_shape(data) != self.dimensions:
            #TODO This will probably need to be more sophisticated
            reasons.append('incorrect shape')
        if not isinstance(get_value(data), self.data_type)
            #TODO copied and pasted from AttributeValidator.validate 
            # will probably need to tailor to datasets needs
            reasons.append('incorrect data type')
        return tuple(reasons)
        


class AttributeValidator(object):
    def __init__(self, spec):
        self.data_type = spec['data_type']
        if 'dimensions' in spec:
            self.dimensions = spec['dimensions']
        else:
            self.dimensions = ()
    
    def validate(self, spec):
        reasons = list()
        if get_shape(spec['value']) != self.dimensions:
            #TODO This will probably need to be more sophisticated
            
            reasons.append('incorrect shape')
        if not isinstance(get_value(spec['value']), self.data_type)
            reasons.append('incorrect data type')
            
        return tuple(reasons)
        
        
def get_shape(data):
    #TODO write this function
    pass

def get_value(data):
    #TODO write this function
    pass

