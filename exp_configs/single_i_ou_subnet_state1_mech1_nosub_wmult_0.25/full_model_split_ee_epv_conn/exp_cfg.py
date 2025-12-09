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

POPS_E = ['IT2', 'IT3', 'ITS4', 'ITP4', 'IT5A', 'CT5A',
          'IT5B', 'CT5B', 'PT5B', 'IT6', 'CT6']
POPS_PV = ['PV2', 'PV3', 'PV4', 'PV5A', 'PV5B', 'PV6']

EE_FRAC_ACTIVE = 0.5
EPV_FRAC_ACTIVE = 0.5

OU_CTRL = 0


def apply_exp_cfg(cfg, par=None):

    # Duration
    cfg.duration = 10000

    #cfg.saveCellSecs = True
    cfg.cache_efficient = 0

    # Left point (ms) of the calculation time window (r, cv, ...)
    cfg.t0_calc = max(0, cfg.duration - 2000)

    # E->E pop. pairs
    conns_ee = [(pop1, pop2) for pop1 in POPS_E for pop2 in POPS_E]
    conns_ee = list(set(conns_ee))
    # E->PV pop. pairs
    conns_epv = [(pop1, pop2) for pop1 in POPS_E for pop2 in POPS_PV]
    conns_epv = list(set(conns_epv))
    # Combine
    conns_split = {f'{c[0]}, {c[1]}': EE_FRAC_ACTIVE for c in conns_ee}
    conns_split |= {f'{c[0]}, {c[1]}': EPV_FRAC_ACTIVE for c in conns_epv}

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {   
        'pops_active': POPS_ACTIVE,
        'conns_frozen': [],
        'conns_split': conns_split,
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
    with open(dirpath_self / 'ou_inputs.json', 'r') as fid:
        cfg.ou_pop_inputs = json.load(fid)
    
    # Read target rates
    df = pd.read_csv(dirpath_self / 'target_state_1.csv')
    target_rates = df.set_index('pop_name')['target_rate'].to_dict()

    # OU controlled by a rate feedback
    if OU_CTRL:
        cfg.ou_ctrl_params = {
            'mu_gain': 1e-1,
            'sigma_gain': 0.0,
            'tau_ctrl': 200,
            'taus_ctrl': 1000,
            'target_rates': target_rates,
            'k_ctrl': 2e-4,
            'kp_ctrl': 0e-2,
            'z0': 0,
            't0': 2000,
            'tlock': 12000
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

    exp_name_sub = (f'exp_t_{t_limits[0]}_{t_limits[1]}'
                    f'_ee_{EE_FRAC_ACTIVE}_epv_{EPV_FRAC_ACTIVE}')
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
        'raster.png', 'cfg.json', 'netParams.json',
        #'spikeStat_boxplot_rate.png', 'spikeStat_boxplot_isicv.png'
    ]
    for res_name in res_names:
        fname = f'{exp_name}_{res_name}'
        if (dirpath_res / fname).exists():
            (dirpath_res / fname).rename(dirpath_res_sub / fname)
    
    # Move traces to the subfodler
    for fpath in dirpath_res.glob(f'{exp_name}_*traces*.png'):
        fpath.rename(dirpath_res_sub / fpath.name)
    
    # Save rates, CVs, and voltage stats to a json file
    res = proc.calc_rates_and_cvs(sim, t_limits, nspikes_min=3)
    #res |= proc.calc_v_stats(sim, t_limits, med_win=0.05)
    fpath_res = dirpath_res_sub / f'{exp_name}_result.json'
    with open(fpath_res, 'w') as fid:
        json.dump(res, fid, indent=4)
