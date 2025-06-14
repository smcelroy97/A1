import json
from pathlib import Path


dirpath_self = Path(__file__).resolve().parent


def apply_exp_cfg(cfg):

    # Duration
    cfg.duration = 2 * 1e3

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {
        #'pops_active': ['IT5A', 'CT5A', 'PV5A', 'SOM5A', 'VIP5A'],
        'pops_active': 'all',
        'conns_frozen': 'all',
        'fpath_frozen_rates': str(dirpath_self / 'frozen_rates.csv')
    }

    # Weight multiplier
    cfg.wmult = 0.1

    # OU current
    cfg.add_ou_current = 1
    cfg.ou_common = 0
    cfg.ou_noise_duration = cfg.duration
    cfg.ou_tau = 2
    with open(dirpath_self / 'ou_inputs.json', 'r') as fid:
        cfg.ou_pop_inputs = json.load(fid)

    # Initial OU ramp
    #cfg.ou_ramp_dur = None
    cfg.ou_ramp_dur = 500
    cfg.ou_ramp_offset = -3
    cfg.ou_ramp_mult = 0

    # Time range for rate and CV calculation
    cfg.analysis['plotSpikeStats'] = False
