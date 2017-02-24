

class NWBFileReader(BaseObjectHandler):
    @docval({'name': 'nwb_path', 'type': str, 'doc': 'The path to the NWB file to read'})
    def __init__(self, **kwargs):
        nwb_path = getargs('nwb_path', kwargs)
        self.hdf5_file = h5py.File(nwb_path, 'r')

        # build up electrode groups
        self.ec_electrodes = list()
        eg_dataset = self.hdf5_file['/general/extracellular_ephys/electrode_group']
        imp_dataset = self.hdf5_file['/general/extracellular_ephys/impedance']
        loc_dataset = self.hdf5_file['/general/extracellular_ephys/electrode_map']
        ecephys_group = self.hdf5_file['/general/extracellular_ephys']
        for idx, name in enumerate(eg_dataset):
            eg_group = ecephys_group.get(name)
            desc = eg_group['description']
            dev = eg_group['device']
            loc = eg_group['location']
            coord = loc_dataset[idx]
            imp = imp_dataset[idx]
            self.ec_electrodes.append(ElectrodeGroup(name, coord, desc, dev, loc, imp)

        self.nwbfile = NWBFile(...)

    def process(self, obj):
        properties = self.get_object_properties(obj)
        ret = list()
        for prop in properties:
            val = None
            if prop in self.procedures:
                func = self.procedures[prop]
                val = func(self, self.get_object_representation(obj))
            ret.append(val)
        return ret

'''

    for nwb_container_h5obj in file:
        python_type = determine_python_type(nwb_container_h5obj)
        attr_map = TypeMap.get_map(python_type)
        nwb_container_obj = build_constructor_args(attr_map, python_type, nwb_container_h5obj)
'''
    def build_container(self, attr_map, nwb_container_type, h5_object):
        if nwb_container_type is None:
            return None
        object_attributes = dict()
        for name in h5_object:
            sub_object = h5_object.get(name, getlink=True)
            if isinstance(sub_object, h5py.SoftLink):
                sub_object = h5_object[sub_object.path]
                if isinstance(sub_object, h5py.Dataset):
                    parent, parent_type = find_parent_and_type(sub_object)
                    if parent and parent.name in self.seen:
                        object_attributes[attribute_name] = self.seen[parent.name]
                    else:
                        # build parent object, and store in self.seen
                        parent_attr_map = TypeMap.get_map(parent_type)
                        parent_container = self.build_container(parent_attr_map, parent_type, parent)
                        self.seen[parent.name] = parent_container
                        attribute_name = attr_map.get_attribute_nwbcontainer(parent_container)
                        object_attributes[attribute_name] = parent_container
                else:
                    # we have a link to a group
                    pass
            else:
                if isinstance(sub_object, h5py.Dataset):
                    attribute_name, attribute_value = attr_map.get_attribute_h5dataset(name, sub_object)
                    object_attributes[attribute_name] = attribute_value
                else:
                    sub_container_type = self.__determine_python_type(sub_object)
                    if sub_container_type is not None:
                        raise TypeError('%s in %s does not have an NWBContainer subtype' % (name, h5_object.name))
                    sub_attr_map = TypeMap.get_map(sub_container_type)
                    attribute_name = attr_map.get_attribute(sub_attr_map.spec)
                    if sub_object.name in self.seen:
                        subcontainer = self.seen[sub_object.name]
                    else:
                        sub_container = self.build_container(sub_attr_map, sub_container_type, sub_object)
                        # keep track of containers we have already built in case we need to share i.e. something is linked to this
                        self.seen[sub_object.name] = sub_container
                    object_attributes[attribute_name] = sub_container
        for h5_attr_name, h5_attr_val in h5_object.attrs:
            attribute_name, attribute_value = attr_map.get_attribute_h5attr(h5_attr_name, h5_attr_val)
            object_attributes[attribute_name] = attribute_value

        constr_docval = getattr(python_type.__init__, docval_attr_name)
        constr_args = list()
        constr_kwargs = dict()
        for arg in constr_docval:
            name = arg['name']
            if 'default' in arg:
                constr_kwargs[name] = object_attributes[name]
            else:
                constr_args.append(object_attributes[name])
        return nwb_container_type(*constr_args, **constr_kwargs)

    @classmethod
    def __find_dataset_parent(cls, h5_object):
        curr = h5_object
        parent = None
        parent_type = None
        while True:
            parent = curr.parent
            parent_type = cls.__determine_python_type(parent)
            if parent_type is not None:
                break

        return parent, parent_type



def read_file(path):
    f = h5py.File(path, 'r')
    for 

