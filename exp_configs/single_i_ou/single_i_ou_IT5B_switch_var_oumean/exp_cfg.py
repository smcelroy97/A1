import json
import os
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np

dirpath_self = Path(__file__).resolve().parent
dirpath_repo_root = Path(__file__).resolve().parents[3]
sys.path.append(str(dirpath_repo_root))

import analysis.ou_tuning.netpyne_res_parse_utils as parse_utils
import analysis.ou_tuning.data_proc_utils as proc_utils


def apply_exp_cfg(cfg):
    """Applied after default cfg creation and before netParams creation. """

    # Duration
    cfg.duration = 7 * 1e3
    
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
    cfg.OUamp = [0, 0.2]
    #cfg.OUstd = 0.005
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
    cfg.ou_ramp_t0 = 3500
    cfg.ou_ramp_offset = 2
    cfg.ou_ramp_mult = 1
    #cfg.ou_ramp_type = 'up_down'
    cfg.ou_ramp_type = 'up'


def modify_net_params(cfg, params):
    """Applied after netParams creation. """
    
    mechs = params.cellParams['IT5B_reduced']['secs']['soma'] ['mechs']
    #mechs['kBK']['gpeak'] = 5e-03
    #mechs['kBK']['tau'] = 20
    mechs['kdr']['gbar'] = 0.02
    #mechs['cadad']['taur'] = 100
    mechs['nax']['gbar'] = 0.1


def post_run(sim):
    """Called in the end of a job (after runnig and saving). """

    pop = 'IT5B'
    time_ranges = [(2.5, 3.5), (6, 7)]    

    sim_result = parse_utils.prepare_sim_result(sim)
    spikes = parse_utils.get_pop_spikes(sim_result, pop, combine_cells=False)

    avg_rates = []
    for n, t_range in enumerate(time_ranges):
        rr = proc_utils.calc_pop_rate(spikes, t_range)
        avg_rates.append(rr)
    
    ncells = len(spikes)
    ouamp_min, ouamp_max = sim.cfg.OUamp
    ou_amps = np.linspace(ouamp_min, ouamp_max, ncells)
    
    plt.figure(figsize=(12, 6))
    for n, t_range in enumerate(time_ranges):
        plt.plot(ou_amps, np.array(avg_rates[n]) + n, '.',
                 label=f't=({t_range[0]}-{t_range[1]})')
    plt.xlabel('OU amplitude')
    plt.ylabel('Avg. rate (Hz)')
    plt.title(f'Pop: {pop}')
    plt.legend()

    cfg = sim.cfg
    mechs = sim.net.params.cellParams['IT5B_reduced']['secs']['soma'] ['mechs']

    exp_name = dirpath_self.name
    dirpath_res = dirpath_repo_root / 'exp_results' / 'single_i_ou' / exp_name
    os.makedirs(dirpath_res, exist_ok=True)
    fname_out = (
        'ir_avg'
        f'_oustd_{cfg.OUstd * 100 : .02f}'
        f'_ramp_{cfg.ou_ramp_offset}'
        f'_gkdr_{mechs["kdr"]["gbar"]}'
        #f'_gkbk_{mechs["kBK"]["gpeak"] * 100 : .03f}'
        #f'_taucadad_{mechs["cadad"]["taur"]}'
        f'_gnax_{mechs["nax"]["gbar"]}'
        '.png'
    )
    plt.savefig(dirpath_res / fname_out, dpi=300)
