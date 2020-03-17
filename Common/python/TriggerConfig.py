import json

def Load(file_name):
    with open(file_name) as f:
        trig_desc = json.load(f)
    channel_triggers = {}
    for trig_name, desc in trig_desc.iteritems():
        if 'target_channels' in desc:
            for channel in desc['target_channels']:
                if channel not in channel_triggers:
                    channel_triggers[channel] = []
                desc['name'] = trig_name
                channel_triggers[channel].append(desc)
    return trig_desc, channel_triggers

def LoadAsVPSet(file_name):
    import FWCore.ParameterSet.Config as cms
    with open(file_name) as f:
        trig_desc = json.load(f)
    trig_vpset = cms.VPSet()
    tag_path_names = []
    for trig_name, desc in trig_desc.iteritems():
        filters = [ str(','.join(path_list)) for path_list in desc['filters'] ]
        is_tag = 'is_tag' in desc and desc['is_tag'] > 0
        leg_types = [ str(leg_type) for leg_type in desc['leg_types'] ]
        pset = cms.PSet(
            path = cms.string(str(trig_name)),
            filters = cms.vstring(filters),
            leg_types = cms.vstring(leg_types),
            is_tag = cms.bool(is_tag)
        )
        trig_vpset.append(pset)
        if is_tag:
            tag_path_names.append(str(trig_name))
    return trig_vpset, tag_path_names
