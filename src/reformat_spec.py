import os
import sys
import json
import yaml

#pynwb_path = os.path.abspath('../')
#print(pynwb_path)
#sys.path.append(pynwb_path)
import pynwb
from pynwb.io.spec import Spec, AttributeSpec, BaseStorageSpec, DatasetSpec, GroupSpec, SpecCatalog

def build_group(name, d):
    required = True
    myname = name
    if myname[-1] == '?':
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
    if 'attributes' in d:
        attributes = d.pop('attributes', None)
        nwb_type = None
        if 'neurodata_type' in attributes:
            nwb_type = attributes['neurodata_type']['value']
        grp_spec = GroupSpec(name, required=required, doc=desc, nwb_type=nwb_type)
        add_attributes(grp_spec, attributes)
    else:
        grp_spec = GroupSpec(name, required=required, doc=desc)
    for key, value in d.items():
        name = key
        if isinstance(value, str) or key == 'merge':
            continue
        if key.rfind('/') == -1:
            grp_spec.set_dataset(build_dataset(name, value))
        else:
            grp_spec.set_group(build_group(name, value))
    return grp_spec

def build_dataset(name, d):
    kwargs = remap_keys(name, d)
    dset_spec = DatasetSpec(kwargs.pop('dtype'), name=name, **kwargs)
    if 'attributes' in d:
        add_attributes(dset_spec, d['attributes'])
    return dset_spec

def add_attributes(parent_spec, attributes):
    for attr_name, attr_spec in attributes.items():
        parent_spec.set_attribute(build_attribute(attr_name, attr_spec))

def build_attribute(name, d):
    kwargs = remap_keys(name, d)
    attr_spec = AttributeSpec(name, kwargs.pop('dtype'), **kwargs)
    return attr_spec

def remap_keys(name, d):
    ret = dict()
    ret['required'] = True
    if name == '?':
        ret['required'] = False
    ret['const'] = d.get('const', None)
    ret['dtype'] = d.get('data_type', 'None')
    
    ret['default'] = d.get('value', None)
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
    
    root = GroupSpec(nwb_type='NWBFile')
    acquisition = root.set_group(build_group('acquisition', spec['/acquisition/']))
    analysis = root.set_group(build_group('analysis', spec['/analysis/']))
    epochs = root.set_group(build_group('epochs', spec['/epochs/']))

    processing = root.set_group(build_group('processing', spec['/processing/']))
    stimulus = root.set_group(build_group('stimulus', spec['/stimulus/']))
    general = root.set_group(build_group('general', spec['/general/']))
    extracellular_ephys = general.set_group(build_group('extracellular_ephys?', spec['/general/extracellular_ephys/?']))
    intracellular_ephys = general.set_group(build_group('intracellular_ephys?', spec['/general/intracellular_ephys/?']))
    optogenetics = general.set_group(build_group('optogenetics?', spec['/general/optogenetics/?']))
    optophysiology = general.set_group(build_group('optophysiology?', spec['/general/optophysiology/?']))

    # load TimeSeries specs
    ts_types = [
        "<AbstractFeatureSeries>/",
        "<AnnotationSeries>/",
        "<CurrentClampSeries>/",
        "<CurrentClampStimulusSeries>/",
        "<ElectricalSeries>/",
        "<IZeroClampSeries>/",
        "<ImageMaskSeries>/",
        "<ImageSeries>/",
        "<IndexSeries>/",
        "<IntervalSeries>/",
        "<OpticalSeries>/",
        "<OptogeneticSeries>/",
        "<PatchClampSeries>/",
        "<RoiResponseSeries>/",
        "<SpatialSeries>/",
        "<SpikeEventSeries>/",
        "<TimeSeries>/",
        "<TwoPhotonSeries>/",
        "<VoltageClampSeries>/",
        "<VoltageClampStimulusSeries>/"
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
        for m in merge:
            merge_spec(m, ts_spec)
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
        merge = mod_spec.pop('merge')
        mod_specs[mod] = build_group(mod, mod_spec)
        merge_spec(mod_specs[mod], iface)
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
    return ret


def load_iface(spec):
    spec = spec['fs']['core']['schema']
    iface = build_group('*', spec['<Interface>/'])
    return iface

spec_path = sys.argv[1]
with open(spec_path) as spec_in:
    nwb_spec = load_spec(json.load(spec_in))
    #nwb_spec = load_iface(json.load(spec_in))

##print(json.dumps(nwb_spec, indent=4))
print(yaml.dump(json.loads(json.dumps(nwb_spec)), default_flow_style=False))

