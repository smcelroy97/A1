import json
from pathlib import Path


dirpath_self = Path(__file__).resolve().parent


def apply_exp_cfg(cfg):
    
    # Duration
    cfg.duration = 5 * 1e3
    
    # Turn off the connections
    cfg.addConn = 0

    # Populations to use
    cfg.pops_active = [
        'PV4'
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
    cfg.OUamp = 0.002
    cfg.OUstd = 0.01

    # Record voltage traces
    ncells_rec = 10
    ncells_plot = 4
    cfg.recordCells = [(pop, list(range(ncells_rec))) for pop in cfg.allpops]
    cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
    cfg.recordStep =  0.1
    cfg.analysis['plotTraces'] = {
        'include': [(pop, list(range(ncells_plot))) for pop in cfg.allpops],
        'timeRange': [1000, cfg.duration],
        'oneFigPer': 'trace', 'overlay': False,
        'saveFig': True, 'showFig': False, 'figSize': (18, 12)
    }

    # Time range for rate and CV calculation
    cfg.analysis['plotSpikeStats']['timeRange'] = [2000, cfg.duration]

