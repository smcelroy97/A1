import json
from pathlib import Path


dirpath_self = Path(__file__).resolve().parent


def apply_exp_cfg(cfg):

    # Duration
    cfg.duration = 5 * 1e3
    
    # Turn off the connections and bkg inputs
    cfg.addConn = 0
    cfg.addBkgConn = 0

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
    cfg.OUamp = [0, 0.03]
    cfg.OUstd = 0
    #cfg.OUstd = [(x + 0.005) * 0.5 for x in cfg.OUamp]
    #cfg.OUamp = 0.005
    #cfg.OUstd = [0, 0.03]

    # Record voltage traces
    cells_rec = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450]
    cfg.recordCells = [(pop, cells_rec) for pop in cfg.allpops]
    cfg.recordTraces = {
        'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'},
        #'p_kBK': {'sec': 'soma', 'loc': 0.5, 'var': 'p', 'mech': 'kBK'}
        'n_kdr': {'sec': 'soma', 'loc': 0.5, 'var': 'n', 'mech': 'kdr'}
    }
    cfg.recordStep =  0.1
    cfg.analysis['plotTraces'] = {
        'include': [(pop, cells_rec) for pop in cfg.allpops],
        'timeRange': [0, cfg.duration],
        'oneFigPer': 'cell', 'overlay': False,
        'saveFig': True, 'showFig': False, 'figSize': (18, 12)
    }

    # OU ramp
    #cfg.ou_ramp_dur = None
    cfg.ou_ramp_dur = 1000
    cfg.ou_ramp_t0 = 1500
    cfg.ou_ramp_offset = 3
    cfg.ou_ramp_mult = 1
    #cfg.ou_ramp_type = 'up_down'
    cfg.ou_ramp_type = 'up'


def modify_net_params(cfg, params):
    
    kbk = params.cellParams['IT5B_reduced']['secs']['soma'] ['mechs']['kBK']
    kdr = params.cellParams['IT5B_reduced']['secs']['soma'] ['mechs']['kdr']
    #kbk['gpeak'] = 5e-03
    #kbk['tau'] = 20
    kdr['gbar'] = 0.04

    #pass
