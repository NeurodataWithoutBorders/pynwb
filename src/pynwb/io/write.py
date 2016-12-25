from pynwb.ui.container import NwbContainer
from pynwb.ui.timeseries import TimeSeries, ElectricalSeries, SpatialSeries, AbstractFeatureSeries
from pynwb.ui.epoch import Epoch, EpochTimeSeries
from pynwb.ui.module import Module, Clustering
from pynwb.ui.iface import Interface
from pynwb.ui.file import NWBFile
from .h5tools import GroupBuilder, DatasetBuilder, ExternalLinkBuilder, write_group
from .utils import BaseObjectHandler
from .map import TypeMap

import h5py
import numpy as np
import time
import posixpath
import json

def process_spec(builder, spec, value):
    if isinstance(spec, AttributeSpec):
        builder.add_attribute(spec.name, value)
    else:
        if isinstance(spec, DatasetSpec):
            builder.add_dataset(spec.name, value)
        elif isinstance(spec, GroupSpec):
            #TODO: this assumes that value is a Container
            # This is where spec.name comes from -- Containers have a name value
            group_name = spec.name
            attrs = [value]
            if any(isinstance(value, t) for t in (list, tuple, dict)):
                attrs = value
                if isinstance(value, dict):
                    attrs = value.values()
            for container in attrs:
                builder.add_group(container_map.get_group_name(container),
                                  render_container(container, TypeMap.get_map(container)))

def render_container(container, attr_map):
    builder = GroupBuilder()
    children_attributes = dict()
    
    for attr_name in container.nwb_fields:
        tmp_builder = builder
        attr = getattr(container, attr_name)
        #TODO: add something to handle links
        attr_spec = attr_map.get_spec(attr_name)

        # add this after we created the parent
        if attr_spec.parent != attr_map.spec:
            child_attributes.append(attr_name)
        process_spec(tmp_builder, attr_spec, attr)
        
    # add attributes that apply to subgroups and datasets
    for attr_name in children_attributes:
        attr = getattr(container, attr_name)
        attr_spec = attr_map.get_spec(attr_name)
        parent_spec_attr_name = attr_map.get_attribute(attr_spec.parent)
        parent_builder_name = attr_spec.parent.name 
        # TODO: add check for wildcard name
        if parent_builder_name in builder:
            tmp_builder = builder.get(parent_builder_name)
        else:
            #TODO: handle case where parent spec not created yet
            pass
        process_spec(tmp_builder, attr_spec, attr)
        
    return builder



class HDF5Writer(object):
    def __init__(self):
        self.__renderer = NWBFileHDF5Renderer()

    def write(self, nwb_container, file_path):
        """ This function takes a NWB object and a file_path,
            and writes the NWB file in HDF5
        """
        f = h5py.File(file_path, 'w')
        builder = self.__renderer.process(nwb_container)
        links = dict()
        for name, grp_builder in builder.groups.items():
            tmp_links = write_group(f, name, 
                                    grp_builder.groups,
                                    grp_builder.datasets,
                                    grp_builder.attributes,
                                    grp_builder.links)
            links.update(tmp_links)
            
        for link_name, link_builder in links.items():
            if isinstance(link_builder, ExternalLinkBuilder):
                f[link_name] = h5py.ExternalLink(link_builder.file_path, link_builder.path)
            elif link_builder.hard:
                f[link_name] = f[link_builder.path]
            else:
                f[link_name] = h5py.SoftLink(link_builder.path)
        f.close()

class HDF5ContainerRenderer(BaseObjectHandler):

    def __init__(self):
        pass

    @classmethod
    def get_object_properties(cls, container):
        exclude = (object, NwbContainer)
        mro = reversed(container.__class__.__mro__[:-1])
        mro = filter(lambda x: x not in exclude, mro)
        return list(mro)

    def process(self, container):
        result = super(HDF5ContainerRenderer, self).process(container)
        ret = result[0]
        for builder in result[1:]:
            ret.deep_update(builder)
        return ret

    @classmethod
    def datatype(cls, prop):
        return cls.procedure_ext(prop)

    @staticmethod
    def relative_location(parent, child):
        if isinstance(child, NWBFile):
            return ""
        if isinstance(parent, NWBFile):
            if isinstance(child, TimeSeries):
                relpath = None
                if parent.is_rawdata(child):
                    relpath = "acquisition/timeseries"
                elif parent.is_stimulus(child):
                    relpath = "stimulus/presentation"
                elif parent.is_stimulus_template(child):
                    relpath = "stimulus/templates"
                return posixpath.join(relpath, child.name)
            elif isinstance(child, Module):
                return posixpath.join('processing', child.name)
        elif isinstance(parent, Module):
            if isinstance(child, Interface):
                return child.name
        elif isinstance(parent, Interface):
            if isinstance(child, TimeSeries):
                return child.name
        raise Exception('No known location for %s in %s' % (str(type(child)), str(type(parent))))

    @staticmethod
    def get_container_location(container):
        location = list()
        curr = container
        top_container = curr
        while curr.parent:
            location.append(HDF5ContainerRenderer.relative_location(curr.parent, curr))
            top_container = curr.parent
            curr = curr.parent

        if not isinstance(top_container, NWBFile):
            raise Exception('highest container not a file: %s (%s) --> ... --> %s (%s)' % (container, type(container), top_container, type(top_container)))
        
        container_source = top_container.container_source
        container_path = '/%s' % posixpath.join(*reversed(location))
        #container_path = posixpath.join(*reversed(location))
        return (container_source, container_path)

class TimeFinder(object):
    def __init__(self, time_intervals):
        self.time_intervals = time_intervals

    def __call__(self, chunk):
        pass

class NWBFileHDF5Renderer(HDF5ContainerRenderer):

    @HDF5ContainerRenderer.procedure(NWBFile)
    def nwb_file(container):
        builder = GroupBuilder()
        builder.set_group('general', GroupBuilder({
                'devices': GroupBuilder(),
                'extracellular_ephys': GroupBuilder(),
                'intracellular_ephys': GroupBuilder(),
                'optogenetics': GroupBuilder(),
                'optophysiology': GroupBuilder(),
                'specifications': GroupBuilder(),
                'subject': GroupBuilder()
                }
            )
        )
        builder.set_group('stimulus', GroupBuilder({
                'template': GroupBuilder(),
                'presentation': GroupBuilder()
                }
            )
        )
        builder.set_group('acquisition', GroupBuilder({
                'timeseries': GroupBuilder(),
                'images': GroupBuilder()
                }
            )
        )
        builder.set_group('epochs', GroupBuilder())
        builder.set_group('processing', GroupBuilder())
        builder.set_group('analysis', GroupBuilder())
    
        builder.add_dataset("nwb_version", DatasetBuilder(container.nwb_version))
        builder.add_dataset("identifier", DatasetBuilder(container.file_id))
        builder.add_dataset("session_description", DatasetBuilder(container.session_description))
        builder.add_dataset("file_create_date", DatasetBuilder([np.string_(time.ctime())], maxshape=(None,), chunks=True, dtype=h5py.special_dtype(vlen=bytes)))
        builder.add_dataset("session_start_time", DatasetBuilder(container.start_time.strftime('%Y-%m-%dT%H:%M:%SZ')))

        epoch_renderer = EpochHDF5Renderer()
        epochs_group_builder = builder['epochs']
        #finders = dict()
        for name, epoch_container in container.epochs.items():
            epoch_builder = epoch_renderer.process(epoch_container)
            epochs_group_builder.set_group(name, epoch_builder)
            #for epts_name, epts_container in epoch_container.timeseries.items():
            #    if not (epts_container.count and epts_container.idx_start):
            #        ts = epts_container.timeseries
            #        #TODO: figure out how to compute this timeseries path
            #        ts_path = HDF5ContainerRenderer.get_container_location(ts)
            #        #tf = finders.setdefault(ts_path, TimeFinder())
            #        #tf.add_interval(epoch_container.start_time, epoch_container.start_time)

        #for dset_path, time_finder in finders.items():
        #    builder[dset_path].add_iter_inspect(time_finder)
    
        ts_renderer = TimeSeriesHDF5Renderer()
        for ts_container in container.rawdata:
            subgroup_builder = builder['acquisition/timeseries']
            ts_group_builder = ts_renderer.process(ts_container)
            subgroup_builder.set_group(name, ts_group_builder)
    
        for ts_container in container.stimulus:
            subgroup_builder = builder['acquisition/stimulus']
            ts_group_builder = ts_renderer.process(ts_container)
            subgroup_builder.set_group(name, ts_group_builder)
    
        for ts_container in container.stimulus_template:
            subgroup_builder = builder['acquisition/stimulus_template']
            ts_group_builder = ts_renderer.process(ts_container)
            subgroup_builder.set_group(name, ts_group_builder)
    
        module_renderer = ModuleHDF5Renderer()
        processing_builder = builder['processing']
        for name, module_container in container.modules.items():
            mod_group_builder = module_renderer.process(module_container)
            processing_builder.set_group(name, mod_group_builder)
    
        return builder


def is_link(container, attr):
    return False

#def render_container(container, attr_map):
#    builder = GroupBuilder()
#    children_attributes = dict()
#    
#    for attr_name in filter(lambda i: i[0] == '_', dir(container)):
#        attr = getattr(container, attr_name)
#        if callable(attr):
#            continue
#        #TODO: add something to handle links
#        attr_spec = attr_map.children.get(attr_name)
#        
#        if isinstance(attr_spec, AttributeSpec):
#            if attr_spec.parent is not spec:
#                children_attributes[attr_name] = attr_spec
#            else:
#                builder.add_attribute(attr_spec.name, attr)
#        else:
#            if isinstance(attr_spec, DatasetSpec):
#                builder.add_dataset(attr_spec.name, attr)
#            elif isinstance(attr_spec, GroupSpec):
#                #TODO: this assumes that attr is a Container
#                # This is where attr_spec.name comes from -- Containers have a name attr
#                group_name = attr_spec.name
#                attrs = [attr]
#                if any(isinstance(attr, t) for t in (list, tuple, dict)):
#                    attrs = attr
#                    if isinstance(attr, dict):
#                        attrs = attr.values()
#                for container in attrs:
#                    builder.add_group(container_map.get_group_name(container),
#                                      render_container(container, TypeMap.get_map(container)))
#    return builder

class TimeSeriesHDF5Renderer(HDF5ContainerRenderer):
    
    @HDF5ContainerRenderer.procedure(TimeSeries)
    def time_series(container):
        builder = GroupBuilder()
        # set top-level metadata
        builder.set_attribute('ancestry', container.ancestry)
        builder.set_attribute('help', container.help)
        builder.set_attribute('description', container.description)
        builder.set_attribute('source', container.source)
        builder.set_attribute('comments', container.comments)
        builder.set_attribute('neurodata_type', "TimeSeries")
    
        #BEGIN Set data
        if isinstance(container.fields['data'], TimeSeries):
            # If data points to another TimeSeries object, then we are linking
            (container_file, container_path) = HDF5ContainerRenderer.get_container_location(container)
            (reference_file, reference_path) = HDF5ContainerRenderer.get_container_location(container.fields['data'])
            data_path = posixpath.join(reference_path, 'data')
            if container_file != reference_file: 
                builder.add_external_link('data', reference_file, data_path)
            else:
                builder.add_soft_link('data', data_path)
        else:
            # else data will be written to file
            data_attrs = {
                "unit": container.unit, 
                "conversion": container.conversion,
                "resolution": container.resolution,
            }
            builder.add_dataset("data", container.fields['data'], attributes=data_attrs)
        #END Set data
        
        #BEGIN Set timestamps
        if container.starting_time:
            builder.add_dataset("starting_time",
                                        container.starting_time, 
                                        attributes={"rate": container.rate, 
                                                    "unit": "Seconds"})
        else:
            if isinstance(container.fields['timestamps'], TimeSeries):
                (container_file, container_path) = HDF5ContainerRenderer.get_container_location(container)
                (reference_file, reference_path) = HDF5ContainerRenderer.get_container_location(container.fields['timestamps'])
                timestamps_path = posixpath.join(reference_path, 'timestamps')
                if container_file != reference_file:
                    builder.add_external_link('data', reference_file, timestamps_path)
                else:
                    builder.add_soft_link('timestamps', timestamps_path)
            else:
                ts_attrs = {"interval": 1, "unit": "Seconds"}
                builder.add_dataset("timestamps", container.fields['timestamps'], attributes=ts_attrs)
        #END Set timestamps
        return builder
    
    @HDF5ContainerRenderer.procedure(AbstractFeatureSeries)
    def abstract_feature_series(container):
        builder = GroupBuilder()
        builder.add_dataset('features', container.features)
        builder.add_dataset('feature_units', container.units)
        return builder
    
    @HDF5ContainerRenderer.procedure(ElectricalSeries)
    def electrical_series(container):
        builder = GroupBuilder()
        builder.add_dataset("electrode_idx", container.electrodes)
        return builder
    
    @HDF5ContainerRenderer.procedure(SpatialSeries)
    def spatial_series(container):
        builder = GroupBuilder()
        builder.add_dataset("reference_frame", container.reference_frame)
        return builder
    

class ModuleHDF5Renderer(HDF5ContainerRenderer):

    @HDF5ContainerRenderer.procedure(Module)
    def module(container):
        builder = GroupBuilder()
        iface_renderer = InterfaceHDF5Renderer()
        for name, interface in container.interfaces.items():
            interface_builder = iface_renderer.process(interface)
            builder.add_group(interface.iface_type, interface_builder)
        return builder
    

class InterfaceHDF5Renderer(HDF5ContainerRenderer):

    @HDF5ContainerRenderer.procedure(Interface)
    def interface(container):
        builder = GroupBuilder()
        builder.set_attribute('help', container.help)
        builder.set_attribute('neurodata_type', "Interface")
        #TODO: Figure out how to appropriately set source
        builder.set_attribute('source', container.source)
        return builder
    
    @HDF5ContainerRenderer.procedure(Clustering)
    def clustering(container):
        builder = GroupBuilder()
        cluster_nums = list(sorted(container.peak_over_rms.keys()))
        peak_over_rms = [container.peak_over_rms[n] for n in cluster_nums]
        builder.add_dataset('cluster_nums', cluster_nums)
        builder.add_dataset('peak_over_rms', peak_over_rms)
        #TODO: verify this works after finishing Clustering interface
        builder.add_dataset('num', container.num)
        builder.add_dataset('times', container.times)
        return builder

class EpochHDF5Renderer(HDF5ContainerRenderer):
    @HDF5ContainerRenderer.procedure(Epoch)
    def epoch(container):
        builder = GroupBuilder()
        builder.add_dataset('start_time', container.start_time)
        builder.add_dataset('stop_time', container.stop_time)
        builder.add_dataset('description', container.description)
        epts_proc = EpochTimeSeriesHDF5Renderer()
        for epts in container.timeseries:
            builder.set_group(epts.name, epts_proc.process(epts))
        return builder
        
class EpochTimeSeriesHDF5Renderer(HDF5ContainerRenderer):
    @HDF5ContainerRenderer.procedure(EpochTimeSeries)
    def epoch_timeseries(container):
        builder = GroupBuilder()
        builder.add_dataset('count', container.count)
        builder.add_dataset('idx_start', container.idx_start)
        ts_src, ts_path = HDF5ContainerRenderer.get_container_location(container.timeseries)
        builder.add_link(container.timeseries.name, ts_path)
        return builder
        
