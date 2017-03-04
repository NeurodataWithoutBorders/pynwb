import os
import sys
import json
#import yaml
from ruamel import yaml

import pynwb
from pynwb.io.spec import Spec, AttributeSpec, BaseStorageSpec, DatasetSpec, GroupSpec, SpecCatalog


ndmap = {
    "<timeseries_X>/*": 'EpochTimeSeries',
    #"<epoch_X>/*": 'Epoch', # TODO: Figure out how to remove this spec's name
    "<device_X>*": 'Device',
    "<specification_file>*": 'SpecFile',
    "<electrode_group_X>": 'ElectrodeGroup',
    "<electrode_X>": 'IntracellularElectrode',
    "<site_X>/*": 'OptogeneticStimulusSite',
    "<channel_X>": 'OpticalChannel',
    "<imaging_plane_X>/*": 'ImagingPlane',
    "<unit_N>/+": 'SpikeUnit',
    #"<image_name>/+": , # TODO: Figure out how to move this to a link to an ImagingPlane neurodata_type
    "<roi_name>/*": 'ROI',
    "<image_plane>/*": 'SegmentedImagingPlane',
}

all_specs = dict()


def build_group_helper(**kwargs):
    myname = kwargs.pop('name', '*')
    if myname == '*':
        grp_spec = GroupSpec(**kwargs)
    else:
        grp_spec = GroupSpec(name=myname, **kwargs)
    return grp_spec

def build_group(name, d, ndtype=None):
    #print('building %s' % name, file=sys.stderr)
    required = True
    myname = name
    if myname[-1] == '?':
        required = False
        myname = myname[:-1]
    if myname[-1] == '^':
        required = False
        myname = myname[:-1]
    if myname[-1] == '/':
        myname = myname[:-1]
    if myname == '*':
        required = False
    desc = d.get('description', None)
    if isinstance(desc, dict):
        desc = d.pop('_description', None)
    else:
        desc = d.pop('description', None)

    extends = None
    if 'merge' in d:
        merge = d.pop('merge')
        base = merge[0]
        end = base.rfind('>')
        base = base[1:end] if end > 0 else base
        extends = all_specs[base]


    if myname[0] == '<':
        neurodata_type = ndmap.get(myname)
        print('found neurodata_type %s' % neurodata_type, file=sys.stderr)
        if neurodata_type is None:
            neurodata_type = ndtype
        else:
            myname = '*'
        print('neurodata_type=%s, myname=%s' % (neurodata_type, myname), file=sys.stderr)
    else:
        neurodata_type = ndtype
    #TODO: figure out why Interfaces aren't picking up neurodata_type
    if 'attributes' in d:
        attributes = d.pop('attributes', None)
        if 'neurodata_type' in attributes:
            neurodata_type = attributes.pop('neurodata_type')['value']
        elif 'ancestry' in attributes:
            #neurodata_type = attributes['ancestry']['value'][-1]
            neurodata_type = attributes.pop('ancestry')['value'][-1]
        if extends is not None:
            if neurodata_type is None:
                neurodata_type = myname
        grp_spec = build_group_helper(name=myname, required=required, doc=desc, neurodata_type=neurodata_type, extends=extends)
        add_attributes(grp_spec, attributes)
    elif neurodata_type is not None:
        grp_spec = build_group_helper(name=myname, required=required, doc=desc, neurodata_type=neurodata_type, extends=extends)
    else:
        if myname == '*':
            grp_spec = GroupSpec(required=required, doc=desc, extends=extends)
        else:
            grp_spec = GroupSpec(name=myname, required=required, doc=desc, extends=extends)

    for key, value in d.items():
        name = key
        if name[0] == '_':
            #TODO: figure out how to deal with these reserved keys
            continue
        if isinstance(value, str):
            continue
        if 'link' in value:
            ndt = value['link']['target_type']
            if ndt[0] == '<':
                ndt = ndt[1:ndt.rfind('>')]
            else:
                ndt = ndt[0:-1]
            grp_spec.add_link(GroupSpec(neurodata_type=ndt))

        if key.rfind('/') == -1:
            grp_spec.set_dataset(build_dataset(name, value))
        else:
            grp_spec.set_group(build_group(name, value))

    if neurodata_type is not None:
        #print('adding %s to all_specs' % neurodata_type, file=sys.stderr)
        all_specs[neurodata_type] = grp_spec
    #else:
    #    print('no neurodata_type found for %s' % myname, file=sys.stderr)
    return grp_spec

def build_dataset(name, d):
    kwargs = remap_keys(name, d)
    dset_spec = DatasetSpec(kwargs.pop('dtype'), name=name, **kwargs)
    if 'attributes' in d:
        add_attributes(dset_spec, d['attributes'])
    return dset_spec

def add_attributes(parent_spec, attributes):
    if parent_spec.neurodata_type == 'ElectricalSeries':
        print(attributes, file=sys.stderr)
    for attr_name, attr_spec in attributes.items():
        parent_spec.set_attribute(build_attribute(attr_name, attr_spec))

def build_attribute(name, d):
    kwargs = remap_keys(name, d)
    myname = name
    if myname[-1] == '?':
        myname = myname[:-1]
    if myname[-1] == '^':
        myname = myname[:-1]
    attr_spec = AttributeSpec(myname, kwargs.pop('dtype'), **kwargs)
    return attr_spec

def remap_keys(name, d):
    ret = dict()
    ret['required'] = True
    if name[-1] == '?':
        ret['required'] = False
    ret['const'] = d.get('const', None)
    ret['dtype'] = d.get('data_type', 'None')

    ret['value'] = d.get('value', None)
    ret['doc'] = d.get('description', None)
    ret['dim'] = d.get('dimensions', None)

    return ret



def merge_spec(target, source):
    for grp_spec in source.groups:
        target.set_group(grp_spec)
    for dset_spec in source.datasets:
        target.set_dataset(dset_spec)
    for attr_spec in source.attributes:
        target.set_attribute(attr_spec)

def load_spec(spec):

    spec = spec['fs']['core']['schema']

    # load Module specs
    # load File spec
    # /
    # /acquisition/
    # /analysis/
    # /epochs/
    # /general/
    # /general/extracellular_ephys/?
    # /general/intracellular_ephys/?
    # /general/optogenetics/?
    # /general/optophysiology/?
    # /processing/
    # /stimulus/

    #root = GroupSpec(neurodata_type='NWBFile')
    root = build_group('root', spec['/'], 'NWBFile')
    #root.set_dataset(build_dataset('file_create_date',


    acquisition = build_group('acquisition', spec['/acquisition/'])
    root.set_group(acquisition)
    analysis = build_group('analysis', spec['/analysis/'])
    root.set_group(analysis)
    epochs = build_group('epochs', spec['/epochs/'])
    root.set_group(epochs)

    module_json =  spec['/processing/'].pop("<Module>/*")

    processing = build_group('processing', spec['/processing/'])
    root.set_group(processing)

    stimulus = build_group('stimulus', spec['/stimulus/'])
    root.set_group(stimulus)

    general = build_group('general', spec['/general/'])
    root.set_group(general)

    extracellular_ephys = build_group('extracellular_ephys?', spec['/general/extracellular_ephys/?'])
    general.set_group(extracellular_ephys)

    intracellular_ephys = build_group('intracellular_ephys?', spec['/general/intracellular_ephys/?'])
    general.set_group(intracellular_ephys)

    optogenetics = build_group('optogenetics?', spec['/general/optogenetics/?'])
    general.set_group(optogenetics)

    optophysiology = build_group('optophysiology?', spec['/general/optophysiology/?'])
    general.set_group(optophysiology)

    base = [
        "<TimeSeries>/", #
        "<Interface>/",
        "<Module>/",
    ]
    base = [
        root,
        build_group('*', module_json, ndtype='Module'),
        build_group('*', spec["<TimeSeries>/"]),
        build_group('*', spec["<Interface>/"])
    ]


    # load TimeSeries specs

    type_specs = dict()
    subspecs = [
        'ec_ephys',
        'ic_ephys',
        'image',
        'ophys',
        'ogen',
        'behavior',
        'misc',
        'retinotopy',
    ]

    type_specs['ec_ephys'] = [
        "<ElectricalSeries>/",
        "<SpikeEventSeries>/",
        "ClusterWaveforms/",
        "Clustering/",
        "FeatureExtraction/",
        "EventDetection/",
        "EventWaveform/",
        "FilteredEphys/",
        "FeatureExtraction/",
        "LFP/",
    ]

    type_specs['ic_ephys'] = [
        "<PatchClampSeries>/",
        "<CurrentClampSeries>/",
        "<IZeroClampSeries>/",
        "<CurrentClampStimulusSeries>/",
        "<VoltageClampSeries>/",
        "<VoltageClampStimulusSeries>/"
    ]

    type_specs['image'] = [
        "<ImageSeries>/",
        "<ImageMaskSeries>/",
        "<OpticalSeries>/",
        "<RoiResponseSeries>/",
        "<IndexSeries>/",
    ]

    type_specs['ophys'] = [
        "<TwoPhotonSeries>/",
        "DfOverF/",
        "Fluorescence/",
        "ImageSegmentation/",
    ]

    type_specs['ogen'] = [
        "<OptogeneticSeries>/",
    ]

    type_specs['behavior'] = [
        "<SpatialSeries>/",
        "BehavioralEpochs/",
        "BehavioralEvents/",
        "BehavioralTimeSeries/",
        "PupilTracking/",
        "EyeTracking/",
        "CompassDirection/",
        "Position/",
        "MotionCorrection/",
    ]

    type_specs['misc'] = [
        "<AbstractFeatureSeries>/",
        "<AnnotationSeries>/",
        "<IntervalSeries>/",
        "UnitTimes/",
    ]


    type_specs['retinotopy'] = [
        "ImagingRetinotopy/",
    ]

    def mapfunc(name):
        if name[0] == '<':
            return build_group('*', spec[name])
        else:
            return build_group(name, spec[name])

    #for key in type_specs.keys():
    for key in subspecs:
        type_specs[key] = list(map(mapfunc, type_specs[key]))

    type_specs['base'] = base
    return type_specs

"""
    mod_types = [
        "BehavioralEpochs/",
        "BehavioralEvents/",
        "BehavioralTimeSeries/",
        "ClusterWaveforms/",
        "Clustering/",
        "CompassDirection/",
        "DfOverF/",
        "EventDetection/",
        "EventWaveform/",
        "EyeTracking/",
        "FeatureExtraction/",
        "FilteredEphys/",
        "Fluorescence/",
        "ImageSegmentation/",
        "ImagingRetinotopy/",
        "LFP/",
        "MotionCorrection/",
        "Position/",
        "PupilTracking/",
        "UnitTimes/",
    ]

    ts_types = [
        "<TimeSeries>/", #
        "<PatchClampSeries>/",
        "<CurrentClampSeries>/", #
        "<IZeroClampSeries>/", #
        "<CurrentClampStimulusSeries>/", #
        "<VoltageClampSeries>/", #
        "<VoltageClampStimulusSeries>/", #
        "<ElectricalSeries>/", #
        "<SpikeEventSeries>/", #
        "<ImageSeries>/", #
        "<ImageMaskSeries>/", #
        "<IndexSeries>/", #
        "<OpticalSeries>/", #
        "<OptogeneticSeries>/", #
        "<RoiResponseSeries>/", #
        "<SpatialSeries>/", #
        "<TwoPhotonSeries>/", #
    ]
    ts_specs = dict()
    while ts_types:
        ts_type = ts_types.pop(0)
        ts_dict = spec[ts_type]
        merge = list()
        all_bases = True
        for merge_type in ts_dict.pop('merge', list()):
            tmp = ts_specs.get(merge_type, None)
            if tmp:
                merge.append(tmp)
            else:
                ts_types.append(ts_type)
                all_bases = False
                break
        if not all_bases:
            continue

        ts_spec = build_group('*', ts_dict)
        #for m in merge:
        #    merge_spec(m, ts_spec)
        ts_specs[ts_type] = ts_spec

    #print ('created specs for all TimeSeries', file=sys.stderr)

    iface = build_group('*', spec['<Interface>/'])
    #print ('created specs for <Interface>', file=sys.stderr)


    mod_specs = dict()

    mod_types = [
        "BehavioralEpochs/",
        "BehavioralEvents/",
        "BehavioralTimeSeries/",
        "ClusterWaveforms/",
        "Clustering/",
        "CompassDirection/",
        "DfOverF/",
        "EventDetection/",
        "EventWaveform/",
        "EyeTracking/",
        "FeatureExtraction/",
        "FilteredEphys/",
        "Fluorescence/",
        "ImageSegmentation/",
        "ImagingRetinotopy/",
        "LFP/",
        "MotionCorrection/",
        "Position/",
        "PupilTracking/",
        "UnitTimes/",
    ]
    #print ('creating specs for Modules', file=sys.stderr)
    for mod in mod_types:
        mod_spec = spec[mod]
        #merge = mod_spec.pop('merge')
        mod_specs[mod] = build_group(mod, mod_spec)
        #merge_spec(mod_specs[mod], iface)
    #print ('created specs for all Modules', file=sys.stderr)

    #register with SpecMap
    #SpecCatalog.register_spec('NWB', root)
    #SpecCatalog.register_spec('Interface', iface)
    #for ts_type, ts_spec in ts_specs.items():
    #    tmp = ts_type[1:len(ts_type)-2]
    #    SpecCatalog.register_spec(tmp, ts_spec)
    #for mod_type, mod_spec in mod_specs.items():
    #    tmp = mod_type[1:len(mod_type)-1]
    #    SpecCatalog.register_spec(tmp, mod_spec)
    #    pass

    ret = [root, iface]
    ret.extend(ts_specs.values())
    ret.extend(mod_specs.values())
    ret = {'root': list(root.values()), 'Interface': list(iface.values()), 'modules': list(mod_specs.values()), 'timeseries': list(ts_specs.values())}
    return ret



def load_iface(spec):
    spec = spec['fs']['core']['schema']
    iface = build_group('*', spec['<Interface>/'])
    return iface
"""

def represent_str(self, data):
    s = data.replace('"', '\\"')
    return s
    #return self.represent_scalar("", '"%s"' % s)

spec_path = sys.argv[1]
with open(spec_path) as spec_in:
    nwb_spec = load_spec(json.load(spec_in))
    #nwb_spec = load_iface(json.load(spec_in))




for key, value  in nwb_spec.items():
    with open('nwb.%s.yaml' % key, 'w') as out:
        yaml.dump(json.loads(json.dumps(value)), out, default_flow_style=False)

#def quoted_presenter(dumper, data):
#    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='"')

#yaml.add_representer(str, quoted_presenter)
#yaml.add_representer(str, represent_str)
##print(json.dumps(nwb_spec, indent=4))
#print(yaml.dump(json.loads(json.dumps(nwb_spec)), default_flow_style=False, default_style='"'))
#print(yaml.dump(json.loads(json.dumps(nwb_spec)), default_flow_style=False))

