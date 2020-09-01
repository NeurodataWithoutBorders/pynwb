
from hdmf.build import ObjectMapper, TypeMap
from hdmf.build.builders import GroupBuilder


def decode(val):
    if isinstance(val, bytes):
        return val.decode('UTF-8')
    else:
        return val


class ObjectMapperLegacy(ObjectMapper):

    @ObjectMapper.constructor_arg('source')
    def source_gettr(self, builder, manager):

        if 'source' in builder.attributes:
            return builder.attributes['source']
        else:
            return 'No known source'


class TypeMapLegacy(TypeMap):

    def get_builder_dt(self, builder):  # noqa: C901
        '''
        For a given builder, return the neurodata_type.  In this legacy
        TypeMap, the builder may have out-of-spec neurodata_type; this
        function coerces this to a 2.0 compatible version.
        '''

        if builder.name == 'root':
            return 'NWBFile'
        elif builder.name == 'subject' and builder.parent.name == 'general':
            return 'Subject'
        else:

            attrs = builder.attributes
            ndt = attrs.get('neurodata_type')

            if ndt == 'Module':
                return 'ProcessingModule'
            elif ndt == 'Interface':
                return builder.name
            elif ndt == 'Epoch':
                return 'Epoch'
            elif ndt == 'TimeSeries':
                ancestry = decode(attrs['ancestry'][-1])
                if ancestry == 'TwoPhotonSeries' and decode(builder.name) == 'corrected':
                    return 'ImageSeries'
                else:
                    return ancestry
            elif ndt == 'Custom':
                parent_ndt = self.get_builder_dt(builder.parent)
                if parent_ndt == 'ImageSegmentation' and builder.name in ('roi_ids', 'cell_specimen_ids'):
                    return None
                elif parent_ndt == 'PlaneSegmentation' and builder.name in ('roi_list', 'imaging_plane_name'):
                    return None
                elif parent_ndt == 'IntervalSeries' and builder.name in ('frame_duration',):
                    return None
                elif parent_ndt == 'TimeSeries' and builder.name in ('feature_description',
                                                                     'bits_per_pixel',
                                                                     'dimension',
                                                                     'field_of_view',
                                                                     'format'):
                    return None
                elif parent_ndt == 'ImagingPlane' and builder.parent.name in ('imaging_plane_1',):
                    return None
                elif parent_ndt == 'AbstractFeatureSeries' and builder.name in ('frame_duration',):
                    return None
                elif parent_ndt == 'IndexSeries' and builder.name in ('frame_duration',):
                    return None
                elif builder.parent.name == 'general':
                    return None
                elif parent_ndt == 'RoiResponseSeries' and builder.name in ('r',
                                                                            'neuropil_traces_path',
                                                                            'rmse',
                                                                            'comments'):
                    return None
                elif parent_ndt == 'SpatialSeries' and builder.name in ('features'):
                    return None
                else:
                    raise RuntimeError(('Unable to determine neurodata_type: attrs["neurodata_type"]: "Custom",'
                                        'parent.neurodata_type: %s' % parent_ndt))
            else:
                parent_ndt = self.get_builder_dt(builder.parent)
                if parent_ndt == 'Epoch':
                    return 'EpochTimeSeries'
                elif parent_ndt == 'MotionCorrection':
                    return 'CorrectedImageStack'
                elif parent_ndt == 'ImagingPlane' and isinstance(builder, GroupBuilder):
                    return 'OpticalChannel'
                elif parent_ndt == 'ImageSegmentation':
                    return 'PlaneSegmentation'
                elif parent_ndt == 'PlaneSegmentation':
                    if builder.name in ('roi_list', 'imaging_plane_name'):
                        return None
                    else:
                        return 'ROI'
                else:
                    parent_names = {
                        'extracellular_ephys': 'ElectrodeGroup',
                        'intracellular_ephys': 'IntracellularElectrodeGroup',
                        'optophysiology': 'ImagingPlane',
                        'optogenetics': 'OptogeneticStimulusSite',
                        'root': None,
                        'xy_translation': None,
                        'imaging_plane_1': None,
                        'running_speed': None,
                        'general': None,
                        '2p_image_series': None,
                        'natural_movie_one_stimulus': None,
                        'natural_scenes_stimulus': None,
                        'devices': None,
                        'spontaneous_stimulus': None,
                        'static_gratings_stimulus': None,
                        'maximum_intensity_projection_image': None,
                        'imaging_plane_1_neuropil_response': None,
                        'imaging_plane_1_demixed_signal': None,
                        'corrected': None,
                        'running_speed_index': None,
                        'pupil_size_index': None,
                        'pupil_size': None,
                        'pupil_location': None,
                        'pupil_location_spherical': None
                    }
                    return decode(parent_names.get(builder.parent.name))

    def get_builder_ns(self, builder):
        return 'core'
