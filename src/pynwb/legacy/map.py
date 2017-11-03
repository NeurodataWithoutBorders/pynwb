
from ..form.build.map import ObjectMapper, TypeMap
from ..form.build.builders import GroupBuilder


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

    def get_builder_dt(self, builder):

        if builder.name == 'roi_ids':
            pass
        elif builder.name == 'root':
            return 'NWBFile'
        attrs = builder.attributes
        ndt = attrs.get('neurodata_type')
        if ndt == 'Module':
            return 'ProcessingModule'
        elif ndt == 'TimeSeries':
            ancestry = attrs['ancestry']
            if decode(ancestry[-1]) == 'TwoPhotonSeries' and decode(builder.name) == 'corrected':
                return 'ImageSeries'
            else:
                return decode(ancestry[-1])

        elif ndt == 'Interface':
            return builder.name
        if ndt == 'Epoch':
            return 'Epoch'
        else:
            parent_ndt = self.get_builder_dt(builder.parent)
            if parent_ndt == 'Epoch':
                return 'EpochTimeSeries'
            if parent_ndt == 'MotionCorrection':
                return 'CorrectedImageStack'
            if parent_ndt == 'ImagingPlane' and isinstance(builder, GroupBuilder):
                return 'OpticalChannel'
            if parent_ndt == 'ImageSegmentation':
                if builder.name in ('roi_ids', 'cell_specimen_ids'):
                    return None
                else:
                    return 'PlaneSegmentation'

            else:
                if parent_ndt == 'PlaneSegmentation':
                    if builder.name in ('roi_list', 'imaging_plane_name'):
                        return None
                    else:
                        return 'ROI'

                parent_names = {
                    'extracellular_ephys': 'ElectrodeGroup',
                    'intracellular_ephys': 'IntracellularElectrodeGroup',
                    'optophysiology': 'ImagingPlane',
                    'optogenetics': 'OptogeneticStimulusSite'
                }
                return decode(parent_names.get(builder.parent.name))
            return None

    def get_builder_ns(self, builder):
        return 'core'
