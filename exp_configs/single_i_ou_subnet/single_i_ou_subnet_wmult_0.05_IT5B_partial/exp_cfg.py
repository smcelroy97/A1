import json
from pathlib import Path


dirpath_self = Path(__file__).resolve().parent


def apply_exp_cfg(cfg):

    # Duration
    cfg.duration = 5 * 1e3

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {
        'pops_active': ['IT5B'],
        'conns_frozen': 'all',
        #'conns_frozen': [],
        'fpath_frozen_rates': str(dirpath_self / 'frozen_rates.csv'),
        #'duplicate_active_pops': True
        'duplicate_active_pops': False,
        'frozen_rates_custom': {}   # overrides values from csv
    }

    # Turn off some of the surrogate pops.
    pops_pyr = ['IT2', 'IT3', 'IT6', 'ITP4', 'ITS4', 'IT5A',
                'IT5B', 'PT5B', 'CT5A', 'CT5B', 'CT6']
    pops_pv = ['PV2', 'PV3', 'PV4', 'PV5A', 'PV5B', 'PV6']
    pops_som = ['SOM2', 'SOM3', 'SOM4', 'SOM5A', 'SOM5B', 'SOM6']
    pops_vip = ['VIP2', 'VIP3', 'VIP4', 'VIP5A', 'VIP5B', 'VIP6']
    pops_ngf = ['NGF1', 'NGF2', 'NGF3', 'NGF4', 'NGF5A', 'NGF5B', 'NGF6']
    pops_thal = ['TC', 'TCM', 'HTC', 'IRE', 'IREM', 'TI', 'TIM']
    pops_off = pops_pyr + pops_pv + pops_som + pops_vip + pops_ngf + pops_thal
    for pop in pops_off:
        cfg.subnet_params['frozen_rates_custom'][pop] = 0.01
    cfg.subnet_params['frozen_rates_custom']['IT5B'] = 20

    # Weight multiplier
    cfg.wmult = 0.05

    # OU current
    cfg.add_ou_current = 1
    cfg.ou_common = 0
    cfg.ou_noise_duration = cfg.duration
    cfg.ou_tau = 2
    with open(dirpath_self / 'ou_inputs.json', 'r') as fid:
        cfg.ou_pop_inputs = json.load(fid)
    mu = [-0.01, 0.01]
    cfg.ou_pop_inputs['IT5B'] = {
        'ou_mean': mu,
        'ou_std': [(mu_ + 0.01) * 0.2 for mu_ in mu]
        #'ou_std': 0.02
    }
    
    # Initial OU ramp
    cfg.ou_ramp_t0 = 2000
    #cfg.ou_ramp_dur = None
    cfg.ou_ramp_dur = 1000
    cfg.ou_ramp_offset = 0.7
    cfg.ou_ramp_mult = 1
    #cfg.ou_ramp_type = 'up_down'
    cfg.ou_ramp_type = 'up'

    # Time range for rate and CV calculation
    #cfg.analysis['plotSpikeStats']['timeRange'] = [cfg.duration - 1000, cfg.duration]
    cfg.analysis['plotSpikeStats'] = False

    # Record voltage traces
    cells_rec = cells_rec = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450]
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
