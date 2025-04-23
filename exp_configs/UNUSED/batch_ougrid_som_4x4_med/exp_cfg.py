import json
from pathlib import Path


dirpath_self = Path(__file__).resolve().parent


def apply_exp_cfg(cfg):
    
    # Duration
    cfg.duration = 3 * 1e3
    
    # Turn off the connections
    cfg.addConn = 0

    # Populations to use
    cfg.pops_active = [
        'SOM2', 'SOM3', 'SOM4', 'SOM5A','SOM5B', 'SOM6'
    ]
    cfg.allpops = cfg.pops_active
    if 'plotRaster' in cfg.analysis:
        cfg.analysis['plotRaster']['include'] = cfg.pops_active
    if 'plotSpikeStats' in cfg.analysis:
        cfg.analysis['plotSpikeStats']['include'] = cfg.pops_active
    if 'plotTraces' in cfg.analysis:
        cfg.analysis['plotTraces']['include'] = cfg.pops_active

    # Record voltage traces
    ncells_rec = 4
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
    
    # OU conductance
    cfg.add_ou_conductance = 1
    cfg.ou_common = 1    # all pops receive the same OU input
    cfg.NoiseConductanceDur = cfg.duration
    
    # This field will be updated by batchtools
    # (it will be set to a tuple of (OUamp, OUstd))
    cfg.ou_tuple = None
    
    # These fields will be taken from cfg.ou_tuple
    cfg.OUamp = 0    # cfg.ou_tuple[0]
    cfg.OUstd = 0    # cfg.ou_tuple[1]
