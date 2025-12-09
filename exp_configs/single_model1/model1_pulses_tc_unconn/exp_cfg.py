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

from analysis.ou_tuning import sim_res_proc_utils as proc


POPS_ACTIVE = ['TC']


def apply_exp_cfg(cfg, par=None):

    # Duration
    cfg.duration = 15000

    cfg.cache_efficient = 0

    # Left point (ms) of the calculation time window (r, cv, ...)
    cfg.t0_calc = max(0, cfg.duration - 2000)

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {   
        'pops_active': POPS_ACTIVE,
        'conns_frozen': 'all',
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
    with open(dirpath_self / 'ou_inputs_model1.json', 'r') as fid:
        cfg.ou_pop_inputs = json.load(fid)

    # Ovverride the bkg input    
    #cfg.ou_pop_inputs['TC']['ou_mean'] = 0.02
    #cfg.ou_pop_inputs['TC']['ou_std'] = 0.0007
    
    # Read target rates
    df = pd.read_csv(dirpath_self / 'target_state_1.csv')
    target_rates = df.set_index('pop_name')['target_rate'].to_dict()
    cfg.target_rates = target_rates

    # Cell mechanisms to modify
    with open(dirpath_self / 'mech_changes_1.json', 'r') as fid:
        cfg.mech_changes = json.load(fid)

    # Time range for rate and CV calculation
    #cfg.analysis['plotSpikeStats']['timeRange'] = (cfg.t0_calc, cfg.duration)
    cfg.analysis['plotSpikeStats'] = False

    # External stimuli
    cfg.add_pulses = 1
    #rr = np.arange(1000, 20000, 1000).tolist()
    #npulses = len(rr)
    npulses = 10
    cfg.pulse_seq_params = {
        'name': 'PulseSeq',
        'pop': ['TC'],
        't0': 5000,
        'width': 200,
        'n_pulses': npulses,
        #'rates': np.linspace(1000, 20000, npulses).tolist(),
        #'rates': rr,
        #'rates': [500, 1000, 2000, 3000, 4000, 5000, 6000],
        'rates': [5000] * npulses,
        'weight': 0.075,
        'n_cells': 100,
        'convergence': 40,
        'period': 1000,
        'jitter': 0,
        'rand_type': 'norm'
    }

    # Record LFP
    """ cfg.recordTime = True
    cfg.recordStep = 0.2
    cfg.recordLFP = [[100, y, 100] for y in range(0, 2000, 100)]
    layer_bounds= {'L1': 100, 'L2': 160, 'L3': 950, 'L4': 1250,
                   'L5A': 1334, 'L5B': 1550, 'L6': 2000}
    cfg.analysis['plotCSD'] = {
        'spacing_um': 100, 'LFP_overlay': 1, 'layer_lines': 1,
        'layer_bounds': layer_bounds, 'saveFig': 1, 'showFig': 0,
        'timeRange': (2800, cfg.duration)
    } """

    # Record voltage traces
    ncells_rec = 4
    ncells_plot = 4
    cfg.recordCells = [(pop, list(range(ncells_rec))) 
                       for pop in POPS_ACTIVE]
    cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
    cfg.recordStep =  0.1
    cfg.analysis['plotTraces'] = {
        'include': [(pop, list(range(ncells_plot)))
                    for pop in POPS_ACTIVE],
        'timeRange': [1000, cfg.duration],
        'oneFigPer': 'cell', 'overlay': True,
        'saveFig': True, 'showFig': False, 'figSize': (25, 12)
    }

    # Experiment sub-name
    t_limits = (np.round(cfg.t0_calc / 1000), np.round(cfg.duration / 1000))
    exp_name_sub = (f'exp_t_{t_limits[0]}_{t_limits[1]}')
    mu = np.round(cfg.ou_pop_inputs['TC']['ou_mean'] * 100, 2)
    sigma = np.round(cfg.ou_pop_inputs['TC']['ou_std'] * 100, 2)
    exp_name_sub += f'_mu_{mu}_sigma_{sigma}'
    if cfg.add_pulses:
        pulse_par = cfg.pulse_seq_params
        ppop, pt0, pT, pdur, pjit, pjtype, pr, pw, pc = (
            pulse_par['pop'], pulse_par['t0'],
            pulse_par['period'], pulse_par['width'], pulse_par['jitter'],
            pulse_par['rand_type'], pulse_par['rates'], pulse_par['weight'],
            pulse_par['convergence'])
        ppop = '_'.join(ppop)
        if np.isscalar(pr):
            pr0, dpr = pr, 0
        else:
            pr0, dpr = pr[0], np.round(pr[1] - pr[0])
        exp_name_sub += (
            f'_d_{pdur}_T_{pT}_c_{pc}_'
            f'w_{pw}_r_{pr0}_{dpr}_t0_{pt0}_jit_{pjit}')
    #dt_rec, nchan = cfg.recordStep, len(cfg.recordLFP)
    #exp_name_sub += f'_csd_nch_{nchan}_dt_{dt_rec}'
    cfg.exp_name_sub = exp_name_sub


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

    dirpath_res = Path(cfg.saveFolder)

    # Move traces to a subfodler
    os.makedirs(dirpath_res / 'traces', exist_ok=True)
    for fpath in dirpath_res.glob(f'{exp_name}_*traces*.png'):
        fpath.rename(dirpath_res / 'traces' / fpath.name)
    
    # Save rates, CVs, and voltage stats to a json file
    t_limits = (cfg.t0_calc / 1000, cfg.duration / 1000)
    res = proc.calc_rates_and_cvs(sim, t_limits, nspikes_min=3)
    #res |= proc.calc_v_stats(sim, t_limits, med_win=0.05)
    fpath_res = dirpath_res / f'{exp_name}_result.json'
    with open(fpath_res, 'w') as fid:
        json.dump(res, fid, indent=4)
    
    # Plot and save rate dynamics
    r_data = proc.calc_rate_dynamics(
        sim, t_limits=(1.5, None), tau_smooth=0.02, pops_used=POPS_ACTIVE)
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    plt.figure(111); plt.clf()
    r0_lst = []
    for n, pop in enumerate(POPS_ACTIVE):
        tt, rr = r_data[pop]
        r0 = cfg.target_rates[pop]
        r0_lst.append(r0)
        plt.plot(tt, rr, label=pop, color=colors[n])
        plt.plot([tt[0], tt[-1]], [r0, r0], '--', color=colors[n])
    plt.xlabel('Time, s')
    plt.ylabel('Firing rate, Hz')
    plt.legend(bbox_to_anchor=(1, 1))
    plt.yscale('log')
    rmin = np.maximum(0.001, 0.5 * np.min(r0_lst))
    plt.ylim(rmin, None)
    plt.savefig(
        dirpath_res / f'rvec.png',
        dpi=300, bbox_inches='tight'
    )
