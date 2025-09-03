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


def apply_exp_cfg(cfg, par=None):

    # Duration
    cfg.duration = 10 * 1e3

    # Left point (ms) of the calculation time window (r, cv, ...)
    cfg.t0_calc = 8000

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {
        'pops_active': [],   # will be set in batch_params.py
        'conns_frozen': [],  # all conns between active pops are active
        'fpath_frozen_rates': str(dirpath_self / 'target_state_1.csv'),   # surrogate input
    }
    cfg.pop_group_active = ''   # batch parameter

    # Weight multiplier
    cfg.wmult = 0.1

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
    
    # External stimulus
    cfg.add_pulses = 1
    cfg.pulse_seq_params = {
        'name': 'Pulse1',
        'pop': ['ITS4'],
        't0': 4000,
        'width': 500,
        'n_pulses': 1,
        'rates': [1000],
        'weight': 5,
        'n_cells': 1000,
        'convergence': 1,
        'period': 1e5
    }

    # Time range for rate and CV calculation
    cfg.analysis['plotSpikeStats']['timeRange'] = (cfg.t0_calc, cfg.duration)
    #cfg.analysis['plotSpikeStats'] = False
    
    # Initial OU ramp
    """ cfg.ou_ramp_dur = 1000
    cfg.ou_ramp_offset = -1
    #cfg.ou_ramp_offset = 0
    cfg.ou_ramp_mult = 1 """


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

    # Generate filename postfix with param values
    exp_id = exp_name.split('_')[-1]
    postfix = (f'{exp_id}_{cfg.pop_group_active}_'
               f't_{t_limits[0]}_{t_limits[1]}')

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
    trace_files = list(dirpath_res.glob(f'{exp_name}*_traces*.png'))
    for fpath_old in trace_files:
        fpath_new = dirpath_res_sub / 'traces' / fpath_old.name
        fpath_old.rename(fpath_new)
    
    # Move rate and CV boxplots to subfolders
    for fpath_old in dirpath_res.glob(f'{exp_name}*_boxplot_rate*.png'):
        fpath_new = dirpath_res_sub / 'rbox' / fpath_old.name
        fpath_old.rename(fpath_new)
    for fpath_old in dirpath_res.glob(f'{exp_name}*_boxplot_isicv*.png'):
        fpath_new = dirpath_res_sub / 'cvbox' / fpath_old.name
        fpath_old.rename(fpath_new)
