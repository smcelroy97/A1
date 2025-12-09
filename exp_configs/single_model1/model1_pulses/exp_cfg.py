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


POPS_ACTIVE = [
    'NGF1',
    'IT2', 'PV2', 'SOM2', 'VIP2', 'NGF2',
    'IT3', 'PV3', 'SOM3', 'VIP3', 'NGF3',
    'ITP4', 'ITS4', 'PV4', 'SOM4', 'VIP4', 'NGF4',
    'IT5A', 'CT5A', 'PV5A', 'SOM5A', 'VIP5A', 'NGF5A',
    'IT5B', 'CT5B' , 'PT5B', 'PV5B', 'SOM5B', 'VIP5B', 'NGF5B',
    'IT6', 'CT6', 'PV6', 'SOM6', 'VIP6', 'NGF6',
    'TC', 'TCM', 'HTC', 'TI', 'TIM', 'IRE', 'IREM'
]

POP_GROUPS = {
    'L2': ['IT2', 'PV2', 'SOM2', 'VIP2', 'NGF2'],
    'L3': ['IT3', 'PV3', 'SOM3', 'VIP3', 'NGF3'],
    'L4': ['ITP4', 'ITS4', 'PV4', 'SOM4', 'VIP4', 'NGF4'],
    'L5A': ['IT5A', 'CT5A', 'PV5A', 'SOM5A', 'VIP5A', 'NGF5A'],
    'L5B': ['IT5B', 'CT5B' , 'PT5B', 'PV5B', 'SOM5B', 'VIP5B', 'NGF5B'],
    'L6': ['IT6', 'CT6', 'PV6', 'SOM6', 'VIP6', 'NGF6'],
    'Thal': ['TC', 'TCM', 'HTC', 'TI', 'TIM', 'IRE', 'IREM'],
    'Thal2': ['TC', 'IRE'],
    'FF': ['TC', 'ITS4', 'ITP4', 'IT3'],
}

POPS_E = ['IT2', 'IT3', 'ITS4', 'ITP4', 'IT5A', 'CT5A',
          'IT5B', 'CT5B', 'PT5B', 'IT6', 'CT6']

EE_FRAC_ACTIVE = 0.5


def apply_exp_cfg(cfg, par=None):

    # Duration
    cfg.duration = 5000

    cfg.cache_efficient = 0

    # Left point (ms) of the calculation time window (r, cv, ...)
    cfg.t0_calc = max(0, cfg.duration - 2000)

    # Subnet parameters
    conns_ee = [(pop1, pop2) for pop1 in POPS_E for pop2 in POPS_E]
    conns_ee = list(set(conns_ee))
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {   
        'pops_active': POPS_ACTIVE,
        'conns_frozen': [],
        'conns_split': {f'{c[0]}, {c[1]}': EE_FRAC_ACTIVE for c in conns_ee},
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
    npulses = 3
    cfg.pulse_seq_params = {
        'name': 'PulseSeq',
        'pop': ['TC'],
        't0': 2000,
        'width': 200,
        'n_pulses': npulses,
        #'rates': np.linspace(10000, 20000, npulses).tolist(),
        'rates': [2000, 3000, 4000],
        'weight': 5,
        'n_cells': 100,
        'convergence': 2,
        'period': 1000,
        'jitter': 0,
        'rand_type': 'norm'
    }

    # Record LFP
    cfg.recordTime = True
    cfg.recordStep = 0.2
    cfg.recordLFP = [[100, y, 100] for y in range(0, 2000, 100)]
    layer_bounds= {'L1': 100, 'L2': 160, 'L3': 950, 'L4': 1250,
                   'L5A': 1334, 'L5B': 1550, 'L6': 2000}
    cfg.analysis['plotCSD'] = {
        'spacing_um': 100, 'LFP_overlay': 1, 'layer_lines': 1,
        'layer_bounds': layer_bounds, 'saveFig': 1, 'showFig': 0,
        'timeRange': (2800, cfg.duration)
    }

    # Record voltage traces
    ncells_rec = 4
    ncells_plot = 4
    cfg.recordCells = [(pop, list(range(ncells_rec))) 
                       for pop in POP_GROUPS['FF']]
    cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
    cfg.recordStep =  0.1
    cfg.analysis['plotTraces'] = {
        'include': [(pop, list(range(ncells_plot)))
                    for pop in POP_GROUPS['FF']],
        'timeRange': [1000, cfg.duration],
        'oneFigPer': 'cell', 'overlay': True,
        'saveFig': True, 'showFig': False, 'figSize': (18, 12)
    }


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

    # Experiment sub-name
    exp_name_sub = (f'exp_t_{t_limits[0]}_{t_limits[1]}')
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
            f'_pulses_{ppop}_d_{pdur}_T_{pT}_c_{pc}_'
            f'w_{pw}_r_{pr0}_{dpr}_t0_{pt0}_jit_{pjit}')
    dt_rec, nchan = cfg.recordStep, len(cfg.recordLFP)
    exp_name_sub += f'_csd_nch_{nchan}_dt_{dt_rec}'

    # Create a subfolder to put the results
    dirpath_res = Path(cfg.saveFolder)
    dirpath_res_sub = dirpath_res / exp_name_sub
    os.makedirs(dirpath_res_sub, exist_ok=True)

    # Move results to the subfolder
    res_names = [
        'raster.png', 'cfg.json', 'netParams.json', 'data.pkl'
    ]
    for res_name in res_names:
        fname = f'{exp_name}_{res_name}'
        if (dirpath_res / fname).exists():
            (dirpath_res / fname).rename(dirpath_res_sub / fname)
    
    # Move CSD plots to the subfodler
    for fpath in dirpath_res.glob(f'{exp_name}_*CSD.png'):
        fpath.rename(dirpath_res_sub / fpath.name)
    
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
        sim, t_limits=(1.5, None), tau_smooth=0.02, pops_used=POPS_ACTIVE)
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    for group_name, pops in POP_GROUPS.items():
        plt.figure(111); plt.clf()
        r0_lst = []
        for n, pop in enumerate(pops):
            tt, rr = r_data[pop]
            r0 = cfg.target_rates[pop]
            r0_lst.append(r0)
            plt.plot(tt, rr, label=pop, color=colors[n])
            plt.plot([tt[0], tt[-1]], [r0, r0], '--', color=colors[n])
        plt.xlabel('Time, s')
        plt.ylabel('Firing rate, Hz')
        plt.legend(bbox_to_anchor=(1, 1))
        plt.yscale('log')
        rmin = np.maximum(0.05, 0.5 * np.min(r0_lst))
        plt.ylim(rmin, None)
        plt.title(group_name)
        plt.savefig(
            dirpath_res_sub / 'rvec_figs' / f'rvec_{group_name}.png',
            dpi=300, bbox_inches='tight'
        )
