import json
from pathlib import Path


dirpath_self = Path(__file__).resolve().parent


def apply_exp_cfg(cfg):

    # Path to netParams json file
    fpath_net_params = (
        dirpath_self / 
        'par_sub_g_ouinp_wmult_0.005_som4_ire.json'
    )

    # Tell create_net_params.py that netParams should be loaded rather than created
    cfg.netpar_force_load = 1
    cfg.netpar_fpath_json = str(fpath_net_params)

    # Read json
    with open(fpath_net_params, 'r') as f:
        netParams = json.load(f)
    
    # Populations to use
    cfg.pops_active = list(netParams['popParams'].keys())
    cfg.allpops = cfg.pops_active
    if 'plotRaster' in cfg.analysis:
        cfg.analysis['plotRaster']['include'] = cfg.pops_active
    if 'plotSpikeStats' in cfg.analysis:
        cfg.analysis['plotSpikeStats']['include'] = cfg.pops_active
    if 'plotTraces' in cfg.analysis:
        cfg.analysis['plotTraces']['include'] = cfg.pops_active

    # Duration
    cfg.duration = 3 * 1e3
    
    # OU conductance
    cfg.add_ou_conductance = 1
    cfg.ou_common = 0
    cfg.ou_noise_duration = cfg.duration
    cfg.OUamp = 0.002
    cfg.OUstd = 0.01

    # Time range for rate and CV calculation
    cfg.analysis['plotSpikeStats']['timeRange'] = [2000, cfg.duration]
