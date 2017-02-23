

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
                        pass
                else:
                    # we have a link to a group
                    pass
            else:
                if isinstance(sub_object, h5py.Dataset):
                    sub_object_spec = attr_map.spec.get_dataset_spec(name)
                    attribute_name = attr_map.get_attribute(sub_object_spec)
                    object_attributes[attribute_name] = sub_object
                else:
                    sub_container_type = __determine_python_type(sub_object)
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
        for name, h5_attr_val in h5_object.attrs:
            sub_object_spec = attr_map.spec.get_attribute_spec(name)
            attribute_name = attr_map.get_attribute(sub_object_spec)
            object_attributes[attribute_name] = h5_attr_val

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

def __determine_python_type(h5_object):
    name = h5_object.name
    if 'neurodata_type' in h5_object.attrs:
        neurodata_type = h5_object.attrs['']
        if neurodata_type == 'Interface' :
            return Interface.get_extensions(name.split('/')[-1])
        elif neurodata_type == 'TimeSeries' :
            return TimeSeries.get_extensions(h5_object.attrs['ancestry'][-1])
        elif neurodata_type == 'Module' :
            return Module
        elif neurodata_type == 'Epoch' :
            return Epoch
    else:
        if name.startswith('/general/extracellular_ephys'):
            return ElectrodeGroup
        elif name.startswith('/general/intracellular_ephys'):
            return IntracellularElectrode
        elif name.startswith('/general/optogenetics'):
            return OptogeneticSite
        elif name.startswith('/general/optophysiology'):
            name_ar = name[1:].split('/')
            if len(name_ar) == 3:
                return ImagingPlane
            elif len(name_ar) == 4
                return OpticalChannel
    return None

def read_file(path):
    f = h5py.File(path, 'r')
    for 

