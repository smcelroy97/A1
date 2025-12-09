import json
import os
from pathlib import Path
import shutil
import sys

import warnings
warnings.filterwarnings("ignore")

dirpath_repo_root = Path(__file__).resolve().parents[3]
dirpath_self = Path(__file__).resolve().parent
sys.path.append(str(dirpath_repo_root))
sys.path.append(str(dirpath_self))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analysis.ou_tuning import netpyne_res_parse_utils as parse_utils
from analysis.ou_tuning import sim_res_proc_utils as proc
import time


POPS_ACTIVE = ['IT6', 'CT6', 'PV6', 'SOM6', 'VIP6', 'NGF6']
OU_CTRL = 0

OU_INP_LABEL = 'adj1'
OU_INP_PATH = ('exp_results/single_i_ou_subnet_state1_mech1_nosub_wmult_0.25/L6/'
               'exp_t_36.0_40.0_kmu_0.1_ksigma_0.0_tau_200_taus_2500_tc0_2000_'
               'tlock_25000_kci_0.0005_kcp_0.0/ou_inputs_adj.json')


def apply_exp_cfg(cfg, par=None):

    # Duration
    cfg.duration = 40000

    #cfg.saveCellSecs = True
    cfg.cache_efficient = 0

    # Left point (ms) of the calculation time window (r, cv, ...)
    cfg.t0_calc = max(0, cfg.duration - 4000)

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {   
        'pops_active': POPS_ACTIVE,
        'conns_frozen': [],
        'fpath_frozen_rates': str(dirpath_self / 'target_state_1.csv'),
    }    

    # Weight multiplier
    cfg.wmult = 0.25

    # Turn off subConn
    cfg.addSubConn = 0

    # OU current input
    cfg.add_ou_current = 1
    cfg.ou_common = 0
    cfg.ou_noise_duration = cfg.duration
    cfg.ou_tau = 10
    with open(dirpath_repo_root / OU_INP_PATH, 'r') as fid:
        cfg.ou_pop_inputs = json.load(fid)
    
    # Read target rates
    df = pd.read_csv(dirpath_self / 'target_state_1.csv')
    target_rates = df.set_index('pop_name')['target_rate'].to_dict()
    cfg.target_rates = target_rates

    # OU controlled by a rate feedback
    if OU_CTRL:
        cfg.ou_ctrl_params = {
            'mu_gain': 1e-1,
            'sigma_gain': 0.0,
            'tau_ctrl': 200,
            'taus_ctrl': 2500,
            'target_rates': target_rates,
            'k_ctrl': 5e-4,
            'kp_ctrl': 0e-2,
            'z0': 0,
            't0': 2000,
            'tlock': 25000
        }

    # Cell mechanisms to modify
    with open(dirpath_self / 'mech_changes_1.json', 'r') as fid:
        cfg.mech_changes = json.load(fid)

    # Time range for rate and CV calculation
    #cfg.analysis['plotSpikeStats']['timeRange'] = (cfg.t0_calc, cfg.duration)
    cfg.analysis['plotSpikeStats'] = False

    # Record background inputs
    """ ncells_rec = 1
    ncells_plot = 1
    cfg.recordCells = [(pop, list(range(ncells_rec))) for pop in POPS_ACTIVE]
    for pop in POPS_ACTIVE:
        cfg.recordTraces[f'ou_{pop}'] = {
            'sec': 'soma', 'loc': 0.5,
            'var': 'i',
            #'var': 'ctrl',
            'stim': f'NoiseOU_target_{pop}', 
        }
    cfg.recordStep =  0.1
    cfg.analysis['plotTraces'] = {
        'include': [(pop, list(range(ncells_plot))) for pop in POPS_ACTIVE],
        'timeRange': [0, cfg.duration],
        'oneFigPer': 'cell', 'overlay': True,
        'saveFig': True, 'showFig': False, 'figSize': (18, 12)
    } """


def modify_net_params(cfg, params):
    """Applied after netParams creation. """

    # Modify membrane mechanisms
    for v in cfg.mech_changes.values():
        secs_all = params.cellParams[v['pop']]['secs']
        if v['sec'] == 'all':
            secs = list(secs_all.values())
        else:
            secs = [secs_all[v['sec']]]
        for sec in secs:
            sec['mechs'][v['mech']][v['par']] *= v['mult']
            sec['mechs'][v['mech']][v['par']] += v['add']


def post_run(sim):
    """Called in the end of a job (after runnig and saving). """

    cfg = sim.cfg
    exp_name = cfg.simLabel

    # Metric calculation time interval in seconds
    t_limits = (cfg.t0_calc / 1000, cfg.duration / 1000)

    exp_name_sub = (f'exp_{OU_INP_LABEL}_t_{t_limits[0]}_{t_limits[1]}')
    if OU_CTRL:
        par = cfg.ou_ctrl_params
        exp_name_sub += (
            f'_kmu_{par["mu_gain"]}_ksigma_{par["sigma_gain"]}'
            f'_tau_{par["tau_ctrl"]}_taus_{par["taus_ctrl"]}'
            f'_tc0_{par["t0"]}_tlock_{par["tlock"]}'
            f'_kci_{par["k_ctrl"]}_kcp_{par["kp_ctrl"]}'
        )

    # Create a subfolder to put the results
    dirpath_res = Path(cfg.saveFolder)
    dirpath_res_sub = dirpath_res / exp_name_sub
    os.makedirs(dirpath_res_sub, exist_ok=True)

    # Move results to the subfolder
    res_names = [
        'raster.png', 'cfg.json', 'netParams.json', 'data.pkl'
        #'spikeStat_boxplot_rate.png', 'spikeStat_boxplot_isicv.png'
    ]
    for res_name in res_names:
        fname = f'{exp_name}_{res_name}'
        if (dirpath_res / fname).exists():
            (dirpath_res / fname).rename(dirpath_res_sub / fname)
    
    # Move traces to the subfodler
    os.makedirs(dirpath_res_sub / 'traces', exist_ok=True)
    for fpath in dirpath_res.glob(f'{exp_name}_*traces*.png'):
        fpath.rename(dirpath_res_sub / 'traces' / fpath.name)
    
    # Save rates, CVs, and voltage stats to a json file
    res = proc.calc_rates_and_cvs(sim, t_limits, nspikes_min=3)
    #res |= proc.calc_v_stats(sim, t_limits, med_win=0.05)
    fpath_res = dirpath_res_sub / f'{exp_name}_result.json'
    with open(fpath_res, 'w') as fid:
        json.dump(res, fid, indent=4)

    # Plot and save rate dynamics
    os.makedirs(dirpath_res_sub / 'rvec_figs', exist_ok=True)
    r_data = proc.calc_rate_dynamics(
        sim, t_limits=(3, None), tau_smooth=0.5, pops_used=POPS_ACTIVE)
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    plt.figure()
    for n, pop in enumerate(POPS_ACTIVE):
        tt, rr = r_data[pop]
        r0 = cfg.target_rates[pop]
        plt.plot(tt, rr, label=pop, color=colors[n])
        plt.plot([tt[0], tt[-1]], [r0, r0], '--', color=colors[n])
    plt.xlabel('Time')
    plt.ylabel('Firing rate')
    plt.legend(bbox_to_anchor=(1, 1))
    plt.yscale('log')
    plt.ylim(0.05, None)
    plt.savefig(dirpath_res_sub / 'rvec_figs' / f'{exp_name}.png', dpi=300)
    