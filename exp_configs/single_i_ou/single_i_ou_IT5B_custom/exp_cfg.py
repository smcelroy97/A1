import json
from pathlib import Path


dirpath_self = Path(__file__).resolve().parent


def apply_exp_cfg(cfg):

    # Duration
    cfg.duration = 10 * 1e3
    
    # Turn off the connections
    cfg.addConn = 0

    # Populations to use
    cfg.pops_active = [
        'IT5B'
    ]
    cfg.allpops = cfg.pops_active
    if 'plotRaster' in cfg.analysis:
        cfg.analysis['plotRaster']['include'] = cfg.pops_active
    if 'plotSpikeStats' in cfg.analysis:
        cfg.analysis['plotSpikeStats']['include'] = cfg.pops_active
    if 'plotTraces' in cfg.analysis:
        cfg.analysis['plotTraces']['include'] = cfg.pops_active
    
    # OU current
    cfg.add_ou_current = 1
    cfg.ou_common = 1    # all pops receive the same OU input
    cfg.ou_noise_duration = cfg.duration
    cfg.ou_tau = 2
    #cfg.OUamp = [0, 0.025]
    #cfg.OUstd = [(x + 0.005) * 0.5 for x in cfg.OUamp]
    cfg.OUamp = 0.007
    cfg.OUstd = [0, 0.015]

    # Record voltage traces
    cells_rec = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450]
    cfg.recordCells = [(pop, cells_rec) for pop in cfg.allpops]
    cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
    cfg.recordStep =  0.1
    cfg.analysis['plotTraces'] = {
        'include': [(pop, cells_rec) for pop in cfg.allpops],
        'timeRange': [0, cfg.duration],
        'oneFigPer': 'cell', 'overlay': False,
        'saveFig': True, 'showFig': False, 'figSize': (18, 12)
    }

    # Initial OU ramp
    cfg.ou_ramp_t0 = 2000
    #cfg.ou_ramp_dur = None
    cfg.ou_ramp_dur = 2000
    cfg.ou_ramp_offset = 0.2
    cfg.ou_ramp_mult = 1
    #cfg.ou_ramp_type = 'up_down'
    cfg.ou_ramp_type = 'up'
