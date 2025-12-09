import json
import os
from pathlib import Path
import shutil
import sys

dirpath_repo_root = Path(__file__).resolve().parents[3]
dirpath_self = Path(__file__).resolve().parent
sys.path.append(str(dirpath_repo_root))
sys.path.append(str(dirpath_self))

import numpy as np

from analysis.ou_tuning import sim_res_proc_utils as proc

from batch_params import EE_FRAC_ACTIVE_VALS


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

pops_e = ['IT2', 'IT3', 'ITS4', 'ITP4', 'IT5A', 'CT5A',
          'IT5B', 'CT5B', 'PT5B', 'IT6', 'CT6']


def apply_exp_cfg(cfg, par=None):

    # Duration
    cfg.duration = 10 * 1e3

    # Left point (ms) of the calculation time window (r, cv, ...)
    cfg.t0_calc = 8 * 1e3

    conns_ee = [(pop1, pop2) for pop1 in pops_e for pop2 in pops_e]
    conns_ee = list(set(conns_ee))   # remove duplicates

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {
        'pops_active': POPS_ACTIVE,
        'conns_frozen': [],  # all conns between active pops are active
        'conns_split': {f'{c[0]}, {c[1]}': None
                        for c in conns_ee},   # will be set in batch_params.py
        'fpath_frozen_rates': str(dirpath_self / 'target_state_1.csv'),   # surrogate input
    }    
    cfg.ee_frac_active = None   # batch parameter

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

    # Cell mechanisms to modify
    with open(dirpath_self / 'mech_changes_1.json', 'r') as fid:
        cfg.mech_changes = json.load(fid)

    # Time range for rate and CV calculation
    #cfg.analysis['plotSpikeStats']['timeRange'] = (cfg.t0_calc, cfg.duration)
    cfg.analysis['plotSpikeStats'] = False

    # External stimulus
    cfg.add_pulses = 0
    cfg.pulse_seq_params = {
        'name': 'Pulse1',
        'pop': ['IT3'],
        't0': 3500,
        'width': 500,
        'n_pulses': 1,
        'rates': [1000],
        'weight': 5,
        'n_cells': 1000,
        'convergence': 1,
        'period': 1e5
    }
    
    # OU ramp
    """ cfg.ou_ramp_t0 = 0
    cfg.ou_ramp_dur = 4000
    cfg.ou_ramp_offset = -0.4
    #cfg.ou_ramp_offset = 0
    cfg.ou_ramp_mult = 1
    cfg.ou_ramp_pops = ['IT3'] """


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
    kmin, kmax = EE_FRAC_ACTIVE_VALS[0], EE_FRAC_ACTIVE_VALS[-1]
    exp_name_sub = (f'exp_t_{t_limits[0]}_{t_limits[1]}_'
                    f'eefrac_{kmin}_{kmax}')
    if cfg.add_pulses:
        par = cfg.pulse_seq_params
        exp_name_sub += (f'_stim_{par["t0"]}_{par["width"]}_'
                         f'r_{par["rates"][0]}_w_{par["weight"]}')
    if hasattr(cfg, 'ou_ramp_dur'):
        exp_name_sub += (f'_ramp_{cfg.ou_ramp_t0}_{cfg.ou_ramp_dur}_'
                         f'off_{cfg.ou_ramp_offset}_mult_{cfg.ou_ramp_mult}')

    # Generate filename postfix with param values
    exp_id = exp_name.split('_')[-1]
    postfix = (f'{exp_id}_eefrac_{cfg.ee_frac_active}')
    
    # Create subfolders to put the results
    dirpath_res = Path(cfg.saveFolder)
    dirpath_res_sub = dirpath_res / exp_name_sub
    os.makedirs(dirpath_res_sub, exist_ok=True)
    dirnames_sub = ['rasters', 'results', 'cfg', 'traces', 'rbox', 'cvbox']
    for dirname in dirnames_sub:
        os.makedirs(dirpath_res_sub / dirname, exist_ok=True)

    # Rename raster and move it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_raster.png'
    fpath_new = dirpath_res_sub / 'rasters' / f'raster_{postfix}.png'
    if fpath_old.exists():
        fpath_old.rename(fpath_new)

    # Save rates, CVs, and voltage stats to a json file
    res = proc.calc_rates_and_cvs(sim, t_limits, nspikes_min=3)
    res |= proc.calc_v_stats(sim, t_limits, med_win=0.05)
    fpath_res = dirpath_res_sub / 'results' / f'result_{postfix}.json'
    with open(fpath_res, 'w') as fid:
        json.dump(res, fid, indent=4)

    # Rename config file and copy it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_cfg.json'
    fpath_new = dirpath_res_sub / 'cfg' / f'cfg_{postfix}.json'
    shutil.copy(fpath_old, fpath_new)

    # Move traces to a subfolder
    """ trace_files = list(dirpath_res.glob(f'{exp_name}*_traces*.png'))
    for fpath_old in trace_files:
        fpath_new = dirpath_res_sub / 'traces' / fpath_old.name
        fpath_old.rename(fpath_new) """
    
    # Move rate and CV boxplots to subfolders
    """ for fpath_old in dirpath_res.glob(f'{exp_name}*_boxplot_rate*.png'):
        fpath_new = dirpath_res_sub / 'rbox' / fpath_old.name
        fpath_old.rename(fpath_new)
    for fpath_old in dirpath_res.glob(f'{exp_name}*_boxplot_isicv*.png'):
        fpath_new = dirpath_res_sub / 'cvbox' / fpath_old.name
        fpath_old.rename(fpath_new) """
