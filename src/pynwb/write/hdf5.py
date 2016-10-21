from .. import nwbts
from .. import h5tools

import h5py as _h5py


class Hdf5Writer(object):
    def __init__(self):
        self.__renderer = NwbFileRenderer()

    def write(self, nwb_container, file_path):
        f = _h5py.File(file_path, 'w')
        builder = self.__renderer.render(nwb_container)
        links = dict()
        for name, grp_builder in builder.groups.items():
            tmp_links = h5tools.write_group(f, name, 
                                grp_builder.groups,
                                grp_builder.datasets,
                                grp_builder.attributes,
                                grp_builder.links)
            links.update(tmp_links)
            
        for link_name, link_builder in links.items():
            if isinstance(link_builder, h5tools.ExternalLinkBuilder)
                f[link_name] = h5py.ExternalLink(link_builder.file_path, link_builder.path)
            elif link_builder.hard:
                f[link_name] = f[link_builder.path]
            else:
                f[link_name] = h5py.SoftLink(link_builder.path)
        f.close()

class Hdf5ContainerRenderer(object):

    _ts_locations = {
        nwbts.TS_MOD_ACQUISITION: "acquisition/timeseries",
        nwbts.TS_MOD_STIMULUS:    "stimulus/presentation",
        nwbts.TS_MOD_TEMPLATE:    "stimulus/templates",
        nwbts.TS_MOD_OTHER:       ""
    }
            

    def __init__(self):
        pass

    @classmethod
    def container_type(cls, container_type):
        if not hasattr(cls, 'operations'):
            setattr(cls, 'operations', dict())
            setattr(cls, 'rendered', dict())

        def _dec(func):
            cls.operations[container_type] = func
            return func
        return _dec

    @property
    def builder(self):
        return self._builder
    
    def render(self, item):
        self._builder = GroupBuilder()
        self.__render_aux(item.__class__, item)
        self.rendered[item] = self._builder
        return self._builder

    def get_rendered(self, item):
        return self.rendered.get(item, None)

    def __render_aux(self, container_cls, item):
        if container_cls is object:
            return
        for bs_cls in container_type.__bases__:
            self.__render_aux(bs_cls, item)
        if container_cls in self.operations:
            func = self.operations[container_cls]
            func(item)

    @staticmethod
    def __relative_location(parent, child):
        if isinstance(child, nwb.NWBFile):
            return ""
        if isinstance(parent, nwb.NWBFile):
            if isinstance(child, nwbts.TimeSeries):
                mod = parent.get_modality(child)
                return _posixpath.join(_ts_locations[mod], child.name)
            elif isinstance(child, nwbts.Module):
                return _posixpath.join('processing', child.name)
        elif isinstance(parent, nwbmo.Module):
            if isinstance(child, nwbmo.Interface):
                return child.name
        elif isinstance(parent, nwbmo.Interface):
            if isinstance(child, nwbmo.TimeSeries):
                return child.name
        raise Exception('No known location for %s in %s' % (str(type(child)), str(type(parent))))

    @staticmethod
    def get_container_location(container):
        location = list()
        curr = container
        top_container = curr
        while curr.parent:
            location.append(__relative_location(curr.parent, curr))
            top_container = curr
            curr = curr.parent

        if not isinstance(top_container, nwb.NWBFile):
            raise Exception('highest container not a file: %s (%s) --> ... --> %s (%s)' % (None, None, None, None))
        
        container_source = top_container.container_source
        container_path = _posixpath.join(*reversed(location))
        return (container_source, container_path)

class NwbFileRenderer(Hdf5ContainerRenderer):

    def __init__(self, path):
        self._timeseries_renderer = TimeSeriesHdf5Renderer()

    @Hdf5ContainerRenderer.conainer_type(nwbts.TimeSeries)
    def nwb_file(self, container):
        self.builder.add_group('general', GroupBuilder({
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
        self.builder.add_group('stimulus', GroupBuilder({
                'template': GroupBuilder(),
                'presentation': GroupBuilder()
                }
            )
        )
        self.builder.add_group('acquisition', GroupBuilder({
                'timeseries': GroupBuilder(),
                'images': GroupBuilder()
                }
            )
        )
        self.builder.add_group('epochs': GroupBuilder())
        self.builder.add_group('processing': GroupBuilder())
        self.builder.add_group('analysis': GroupBuilder())

        self.builder.add_dataset("nwb_version", DatasetBuilder(FILE_VERSION_STR))
        self.builder.add_dataset("identifier", DatasetBuilder(self.file_identifier))
        self.builder.add_dataset("session_description", DatasetBuilder(self.session_description))
        self.builder.add_dataset("file_create_date", DatasetBuilder([np.string_(time.ctime())], maxshape=(None,), chunks=True, dtype=h5py.special_dtype(vlen=bytes)))
        self.builder.add_dataset("session_start_time", DatasetBuilder(self.start_time))

        for modality, ts_containers in container.timeseries.items():
            subgroup_builder = self.builder[_ts_locations[modality]]
            for name, ts_container in ts_containers:
                ts_group_builder = self._timeseries_renderer.render_item(ts_container)
                subgroup_builder.add_group(name, ts_group_builder)

        processing_builder = builder['processing']
        for name, module_container in self.modules.items():
            mod_group_builder = self._module_renderer.render_item(module_container)
            processing_builder.add_group(name, mod_group_builder)

class TimeSeriesHdf5Renderer(Hdf5ContainerRenderer):
    
    @Hdf5ContainerRenderer.conainer_type(nwbts.TimeSeries)
    def time_series(self, container):
        # set top-level metadata
        self.builder.set_attribute('ancestry', container.ancestry)
        self.builder.set_attribute('help', container.help)
        self.builder.set_attribute('description', container.description)
        self.builder.set_attribute('source', container.source)
        self.builder.set_attribute('comments', container.comments)

        #BEGIN Set data
        if isinstance(container._data, TimeSeries):
            # If data points to another TimeSeries object, then we are linking
            (container_file, container_path) = get_container_location(container)
            (reference_file, reference_path) = get_container_location(container._data)
            data_path = _posixpath.join(reference_path, 'data')
            if container_file != reference_file: 
                self.builder.add_external_link('data', reference_file, data_path)
            else:
                self.builder.add_soft_link('data', data_path)
        else:
            # else data will be written to file
            data_attrs = {
                "unit": unit, 
                "conversion": conversion if conversion else _default_conversion,
                "resolution": resolution if resolution else _default_resolution,
            }
            self.builder.add_dataset("data", container._data, attributes=data_attrs)
        #END Set data
        
        #BEGIN Set timestamps
        if container.starting_time:
            self.builder.add_dataset("starting_time",
                                        container.starting_time, 
                                        attributes={"rate": container.rate, 
                                                    "unit": "Seconds"})
        else:
            if isinstance(container._timestamps, TimeSeries):
                (container_file, container_path) = get_container_location(container)
                (reference_file, reference_path) = get_container_location(container._timeseries)
                timestamps_path = _posixpath.join(reference_path, 'timestamps')
                if container_file != reference_file:
                    self.builder.add_external_link('data', reference_file, timestamps_path)
                else:
                    self.builder.add_soft_link('timestamps', timestamps_path)
            else:
                ts_attrs = {"interval": 1, "unit": "Seconds"}
                self.builder.add_dataset("timestamps", container._timestamps, attributes=ts_attrs)
        #END Set timestamps

    @Hdf5ContainerRenderer.container_type(nwbts.TimeSeries)
    def abstract_feature_series(self, container):
        self.builder.add_dataset('features', container.features)
        self.builder.add_dataset('feature_units', container.units)

    @Hdf5ContainerRenderer.container_type(nwbts.ElectricalSeries)
    def electrical_series(self, container):
        self.builder.add_dataset("electrode_idx", container.electrodes)

    @Hdf5ContainerRenderer.container_type(nwbts.SpatialSeries)
    def spatial_series(self, container):
        self.builder.add_dataset("reference_frame", container.reference_frame)
    


class InterfaceHdf5Renderer(Hdf5ContainerRenderer):
    pass

    
