import json
from pathlib import Path

from netParams_base import cfg, netParams


dirpath_self = Path(__file__).resolve().parent

# Modify membrane mechanisms
v = cfg.mech_changes
for pop in cfg.pops_active:
    secs_all = netParams.cellParams[f'{pop}_reduced']['secs']
    if v['sec'] == 'all':
        secs = list(secs_all.values())
    else:
        secs = [secs_all[v['sec']]]
    for sec in secs:
        sec['mechs'][v['mech']][v['par']] *= v['mult']

# Add NetStim inputs
for pop in cfg.pops_active:
    netParams.stimSourceParams[f'bkg_src_{pop}'] = {
        'type': 'NetStim',
        'rate': cfg.bkg_spike_inputs[pop]['r'],
        'noise': 1.0,
    }
    netParams.stimTargetParams[f'bkg_targ_{pop}'] =  {
        'source': f'bkg_src_{pop}',
        'conds': {'pop': pop},
        'sec': 'apic',
        'loc': 0.5,
        'synMech': 'AMPA',
        'weight': cfg.bkg_spike_inputs[pop]['w']
    }


netParams.save('./old_params.json')