import json
from pathlib import Path


dirpath_self = Path(__file__).resolve().parent


def apply_exp_cfg(cfg):

    # Duration
    cfg.duration = 3 * 1e3

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {
        'pops_active': ['SOM4', 'IRE'],
        'conns_frozen': 'all',
        'fpath_frozen_rates': str(dirpath_self / 'frozen_rates.csv')
    }

    # Weight multiplier
    cfg.wmult = 0.02

    # OU conductance
    cfg.add_ou_conductance = 1
    cfg.ou_common = 0
    cfg.ou_noise_duration = cfg.duration

    # Time range for rate and CV calculation
    cfg.analysis['plotSpikeStats']['timeRange'] = [2000, cfg.duration]
