__all__ = [
    'GroupBuilder',
    'DatasetBuilder',
    'LinkBuilder',
]

import itertools as _itertools
import posixpath as _posixpath
import copy as _copy

SOFT_LINK = 0
HARD_LINK = 1
EXTERNAL_LINK = 2

def set_attributes(obj, attributes):
    for key, value in attributes.iteritems():
        obj.attrs[key] = value

def write_group(parent, name, subgroups, datasets, attributes, links):
    group = parent.create_group(name)
    links_to_create = _copy.deepcopy(links)
    if subgroups:
        for subgroup_name, subgroup_builder in subgroups.iteritems():
            # do not create an empty group without attributes or links
            if subgroup_builder.is_empty():
                continue
            tmp_links = write_group(group,
                            subgroup_name,
                            subgroup_builder.groups,
                            subgroup_builder.datasets,
                            subgroup_builder.attributes,
                            subgroup_builder.links)
            for link_name, target in tmp_links.items():
                if link_name[0] != '/':
                    link_name = _posixpath.join(name, link_name)
                links_to_create[link_name] = target
    if datasets:
        for dset_name, dset_spec in datasets.iteritems():
            write_dataset(group,
                          dset_name,
                          dset_spec.get('data'),
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
    chunks = _itertools.zip_longest(*args, fillvalue=None)
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
        """Create a GroupBuilder object
            Arguments:
                *groups* (string)      a dictionary of subgroups to create in this group
                *datasets* (string)      a dictionary of datasets to create in this group
                *attributes* (string)      a dictionary of attributes to assign to this group
                *links* (string)      a dictionary of links to create in this group
        """
        super().__init__()
        super().__setitem__('groups', groups)
        super().__setitem__('datasets', datasets)
        super().__setitem__('attributes', attributes)
        super().__setitem__('links', links)
        self.obj_type = dict()
        for key in groups.keys():
            self.obj_type[key] = 'groups'
        for key in datasets.keys():
            self.obj_type[key] = 'datasets'
        for key in attributes.keys():
            self.obj_type[key] = 'attributes'
        for key in links.keys():
            self.obj_type[key] = 'links'

    @property
    def groups(self):
        return super().__getitem__('groups')
    
    @property
    def datasets(self):
        return super().__getitem__('datasets')

    @property
    def attributes(self):
        return super().__getitem__('attributes')

    @property
    def links(self):
        return super().__getitem__('links')

    def add_dataset(self, name, data, **kwargs):
        """Add a dataset to this group
            Returns:
                the DatasetBuilder object for the dataset
        """
        super().__getitem__('datasets')[name] = DatasetBuilder(data, **kwargs)
        self.obj_type[name] = 'datasets'
        return super().__getitem__('datasets')[name]
    
    def add_group(self, name, builder=None):
        """Add a subgroup to this group
            Returns:
                the GroupBuilder object for the subgroup
        """
        super().__getitem__('groups')[name] = builder if builder else GroupBuilder()
        self.obj_type[name] = 'group'
        return super().__getitem__('groups')[name]

    def add_hard_link(self, name, path):
        """Add an hard link in this group.

            Arguments:
                *name* (string)      name of the link
                *path* (string)      absolute path to the object to link to

            Returns:
                the LinkBuilder object for the hard link
        """
        super().__getitem__('links')[name] = LinkBuilder(path, hard=True)
        self.obj_type[name] = 'links'
        return super().__getitem__('links')[name]
    
    def add_soft_link(self, name, path):
        """Add an soft link in this group.

            Arguments:
                *name* (string)      name of the link
                *path* (string)      absolute path to the object to link to

            Returns:
                the LinkBuilder object for the soft link
        """
        super().__getitem__('links')[name] = LinkBuilder(path)
        self.obj_type[name] = 'links'
        return super().__getitem__('links')[name]
    
    def add_external_link(self, name, file_path, path):
        """Add an external link in this group.

            Arguments:
                *name* (string)      name of the link
                *file_path* (string) path of the file that contains
                                     the object to link to
                *path* (string)      absolute path to the object to link to

            Returns:
                the LinkBuilder object for the external link
        """
        super().__getitem__('links')[name] = ExternalLinkBuilder(path, file_path)
        self.obj_type[name] = 'links'
        return super().__getitem__('links')[name]
    
    def set_attribute(self, name, value):
        """Set an attribute for this group.
        """
        super().__getitem__('attributes')[name] = value
        self.obj_type[name] = 'attributes'

    def is_empty(self):
        """Returns true if there are no datasets, attributes, links or 
           subgroups that contain datasets, attributes or links. False otherwise.
        """
        if len(super().__getitem__('datasets')) or len(super().__getitem__('attributes')) or len(super().__getitem__('links')):
        #if any(map(lambda k: len(super(dict, self).__getitem__(k)), ('datasets', 'attributes', 'links'))):
            return False
        elif len(super().__getitem__('groups')):
            return all(g.is_empty() for g in super().__getitem__('groups').values())
        else:
            return True

    def __getitem__(self, key):
        """Like dict.__getitem__, but looks in groups,
           datasets, attributes, and links sub-dictionaries.
        """
        try:
            key_ar = _posixpath.normpath(key).split('/')
            return self.__get_rec(key_ar)
        except KeyError:
            raise KeyError(key)

    def get(self, key, default=None):
        """Like dict.get, but looks in groups,
           datasets, attributes, and links sub-dictionaries.
        """
        try:
            key_ar = _posixpath.normpath(key).split('/')
            return self.__get_rec(key_ar)
        except KeyError:
            return default

    def __get_rec(self, key_ar):
        # recursive helper for __getitem__
        if len(key_ar) == 1:
            return super().__getitem__(self.obj_type[key_ar[0]])[key_ar[0]]
        else:
            if key_ar[0] in super().__getitem__('groups'):
                return super().__getitem__('groups')[key_ar[0]].__get_rec(key_ar[1:])
        raise KeyError(key_ar[0])
                

    def __setitem__(self, args, val):
        raise NotImplementedError('__setitem__')

    def __contains__(self, item):
        return self.obj_type.__contains__(item)

    def items(self):
        """Like dict.items, but iterates over key-value pairs in groups,
           datasets, attributes, and links sub-dictionaries.
        """
        return _itertools.chain(super().__getitem__('groups').items(), 
                                super().__getitem__('datasets').items(), 
                                super().__getitem__('attributes').items(),
                                super().__getitem__('links').items())

    def keys(self):
        """Like dict.keys, but iterates over keys in groups, datasets, 
           attributes, and links sub-dictionaries.
        """
        return _itertools.chain(super().__getitem__('groups').keys(), 
                                super().__getitem__('datasets').keys(), 
                                super().__getitem__('attributes').keys(),
                                super().__getitem__('links').keys())

    def values(self):
        """Like dict.values, but iterates over values in groups, datasets, 
           attributes, and links sub-dictionaries.
        """
        return _itertools.chain(super().__getitem__('groups').values(), 
                                super().__getitem__('datasets').values(), 
                                super().__getitem__('attributes').values(),
                                super().__getitem__('links').values())

class LinkBuilder(dict):
    def __init__(self, path, hard=False):
        super().__init__()
        self['path'] = path
        self['hard'] = hard

    @property
    def hard(self):
        return self['hard']

    @property
    def path(self):
        return self['path']


class ExternalLinkBuilder(LinkBuilder):
    def __init__(self, path, file_path):
        super().__init__(path, hard=False)
        self['file_path'] = file_path

    @property
    def file_path(self):
        return self['file_path']

class DatasetBuilder(dict):
    def __init__(self, data, **kwargs):
        super()
        self['data'] = data   
        self['attributes'] = kwargs.pop('attributes', dict())
        for key, value in kwargs.items():
            self[key] = value

    def set_attribute(self, name, value):
        self['attributes'][name] = value
    
    # XXX: leave this here for now, we might want it later
    #def __setitem__(self, args, val):
    #    raise NotImplementedError('__setitem__')
