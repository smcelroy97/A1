import json
from pathlib import Path


dirpath_self = Path(__file__).resolve().parent


def apply_exp_cfg(cfg):

    # Duration
    cfg.duration = 5 * 1e3

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {
        'pops_active': 'all',
        'conns_frozen': 'all',
        'fpath_frozen_rates': str(dirpath_self / 'frozen_rates.csv')
    }

    # Weight multiplier
    cfg.wmult = 0.05
    
    # OU current
    cfg.add_ou_current = 1
    cfg.ou_common = 0
    cfg.ou_noise_duration = cfg.duration
    cfg.ou_tau = 2

    # Time range for rate and CV calculation
    #cfg.analysis['plotRaster'] = False
    #cfg.analysis['plotSpikeStats'] = False
    cfg.analysis['plotSpikeStats']['timeRange'] = [3500, 5000]
