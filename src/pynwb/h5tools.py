import itertools as _itertools
import h5py as _h5py

SOFT_LINK = 0
HARD_LINK = 1
EXTERNAL_LINK = 3

def h5_scalar(func):
    def inner():
        return func().value
    return inner

def sync_files(file1, file2):
    """Create links to datasets and necessary groups
    between file1 and file2
    
    When complete, any dataset in file1 should be linked to
    from file2.
    
    :param file1, file2: The files to sync
    :type file1, file2: h5py.File
    
    """
    pass

class ImmutableGroup(_h5py.Group):
    def __setitem__(self, args, val):
        raise NotImplementedError('__setitem__')

class ImmutableDataset(_h5py.Dataset):
    def __setitem__(self, args, val):
        raise NotImplementedError('__setitem__')

def set_attributes(obj, attributes):
    for key, value in attributes.iteritems():
        obj.attrs[key] = value

def write_group(parent, name, subgroups, datasets, attributes, links):
    group = parent.create_group(name)
    links_to_create = dict()
    if subgroups:
        for subgroup_name, subgroup_spec in subgroups.iteritems():
            tmp_links = write_group(group,
                            subgroup_name,
                            subgroup_spec.get('groups'),
                            subgroup_spec.get('datasets'),
                            subgroup_spec.get('attributes'),
                            subgroup_spec.get('links'))
            for link_name, target in tmp_links.items():
                if link_name[0] != '/':
                    link_name = _posixpath.join(name, link_name)
                links_to_create[link_name] = target
    if datasets:
        for dset_name, dset_spec in datasets.iteritems():
            write_dataset(group,
                          dset_name,
                          dset_spec.get('data')
                          dset_spec.get('attributes'))
    set_attributes(group, attributes)
    return links_to_create

def __get_shape__(data):
    shape = list()
    if hasattr(data, '__len__'):
        shape.append(len(data))
        shape.extend(__get_shape__(data[0]))
    return tuple(shape)

def __get_type__(data):
    if not hasattr(data, '__len__'):
        return type(data)
    else:
        return __get_type__(data[0])

def write_dataset(parent, name, data, attributes):
    if hasattr(data, '__len__'):
        data_shape = __get_shape__(data)
        data_dtype = __get_type__(data)
        dset = parent.require_dataset(name, shape=data_shape, dtype=data_dtype)
        __list_fill__(dset, data)
    else:
        chunk_size = 100
        #TODO: do something to figure out appropriate chunk_size
        #TODO: do something to figure out dtype and shape, and create Dataset
        __iter_fill__(dset, chunk_size, data)
    set_attributes(dest, attributes)
    
def __extend_dataset__(dset):
    new_shape = list(dset.shape)
    new_shape[0] = 2*new_shape[0]
    dset.resize(new_shape)

def __trim_dataset__(dset, length):
    new_shape = list(dset.shape)
    new_shape[0] = length
    dset.resize(new_shape)

def __iter_fill__(dset, chunk_size, data_iter):
    args = [iter(data_iter)] * chunk_size
    chunks = itertools.zip_longest(*args, fillvalue=None)
    idx = 0
    curr_chunk = next(chunks)
    more_data = True
    n_dpts = 0
    while more_data:
        try:
            next_chunk = next(chunks)
        except StopIteration:
            curr_chunk = list(filter(lambda x: x, curr_chunk))
            more_data = False
        if idx >= dset.shape[0] or idx+len(curr_chunk) > dset.shape[0]:
            __extend_dataset__(dset)
        dset[idx:idx+len(curr_chunk),] = curr_chunk
        n_dpts += len(curr_chunk)
        curr_chunk = next_chunk
        idx += chunk_size
    return n_dpts

def __list_fill__(dset, data):
    if len(data) > dset.shape[0]:
        new_shape = list(dset.shape)
        new_shape[0] = len(data)
        dset.resize(new_shape)
    dset[:] = data
    

class GroupBuilder(dict):
    def __init__(self, groups=dict(), datasets=dict(), attributes=dict(), links=dict()):
        self.groups = groups
        self.datasets = datasets
        self.attributes = attributes
        self.links = links
    
    def add_dataset(self, name, data, **kwargs):
        self.datasets[name] = DatasetBuilder(data, **kwargs)
        return self.datasets[name]
    
    def add_group(self, name, builder=GroupBuilder()):
        self.groups[name] = builder

    def add_hard_link(self, name, path):
        self.links[name] = LinkBuilder(HARD_LINK, path)
    
    def add_soft(self, name, path):
        self.links[name] = LinkBuilder(SOFT_LINK, path)
    
    def add_external_link(self, name, file_path, path):
        self.links[name] = LinkBuilder(EXTERNAL_LINK, path, file_path)
    
    def set_attribute(self, name, value):
        self.attributes[name] = value

    def __get_item__(self, key):
        for d in (self.groups, self.datasets, self.attributes, self.links):
            if key in d:
                return d.__get_item__(key)
        raise KeyError(key)

    def __setitem__(self, args, val):
        raise NotImplementedError('__setitem__')

    def get(self, key):
        return self.groups.get(key, 
                               self.datasets.get(key, 
                               self.attributes.get(key,
                               self.links.get(key))))

    def items(self):
        return _itertools.chain(self.groups.items(), 
                                self.datasets.items(), 
                                self.attributes.items(),
                                self.links.items())

    def keys(self):
        return _itertools.chain(self.groups.keys(), 
                                self.datasets.keys(), 
                                self.attributes.keys(),
                                self.links.keys())

    def values(self):
        return _itertools.chain(self.groups.values(), 
                                self.datasets.values(), 
                                self.attributes.values(),
                                self.links.keys())

class LinkBuilder(dict):
    def __init__(self, link_type, path, file_path=None):
        super()
        self['link_type'] = link_type
        self['path'] = path
        self['file_path'] = file_path

class DatasetBuilder(dict):
    def __init__(self, data, **kwargs):
        super()
        self['data'] = data   
        self['attributes'] = kwargs.pop(attributes, dict())
        for key, value in kwargs.items():
            self[key] = value

    def set_attribute(self, name, value):
        self['attributes'][name] = value
    
    # XXX: leave this here for now, we might want it later
    #def __setitem__(self, args, val):
    #    raise NotImplementedError('__setitem__')
