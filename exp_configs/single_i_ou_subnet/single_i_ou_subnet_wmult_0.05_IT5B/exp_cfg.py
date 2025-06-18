import json
from pathlib import Path


dirpath_self = Path(__file__).resolve().parent


def apply_exp_cfg(cfg):

    # Duration
    cfg.duration = 10 * 1e3

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {
        'pops_active': ['IT5B'],
        #'conns_frozen': 'all',
        'conns_frozen': [],
        'fpath_frozen_rates': str(dirpath_self / 'frozen_rates.csv'),
        #'duplicate_active_pops': True
        'duplicate_active_pops': False
    }

    # Weight multiplier
    cfg.wmult = 0.05

    # OU current
    cfg.add_ou_current = 1
    cfg.ou_common = 0
    cfg.ou_noise_duration = cfg.duration
    cfg.ou_tau = 2
    with open(dirpath_self / 'ou_inputs.json', 'r') as fid:
        cfg.ou_pop_inputs = json.load(fid)
    
    # Initial OU ramp
    cfg.ou_ramp_dur = None
    #cfg.ou_ramp_dur = 500
    cfg.ou_ramp_offset = -1
    cfg.ou_ramp_mult = 1

    # Time range for rate and CV calculation
    #cfg.analysis['plotSpikeStats']['timeRange'] = [cfg.duration - 1000, cfg.duration]
    cfg.analysis['plotSpikeStats'] = False

    # Record voltage traces
    #cells_rec = list(range(70, 100))
    cells_rec = list(range(10))
    ncells_rec = len(cells_rec)
    pops_active = cfg.subnet_params['pops_active']
    cfg.recordCells = [(pop, cells_rec) for pop in pops_active]
    cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
    cfg.recordStep = 0.2
    cfg.analysis['plotTraces'] = {
        'include': [(pop, cells_rec) for pop in pops_active],
        #'timeRange': [cfg.duration - 2000, cfg.duration],
        'timeRange': [0, cfg.duration],
        #'oneFigPer': 'trace',
        'oneFigPer': 'cell',
        'overlay': False,
        'saveFig': True, 'showFig': False, 'figSize': (18, 12)
    }
