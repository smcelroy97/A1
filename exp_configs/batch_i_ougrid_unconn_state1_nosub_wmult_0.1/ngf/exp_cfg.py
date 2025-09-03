import json
import os
from pathlib import Path
import shutil
import sys

dirpath_repo_root = Path(__file__).resolve().parents[3]
dirpath_self = Path(__file__).resolve().parent
sys.path.append(str(dirpath_repo_root))
sys.path.append(str(dirpath_self))

from analysis.ou_tuning import sim_res_proc_utils as proc

from batch_params import gen_exp_name_sub


SIM_DURATION = 10 * 1e3
TCALC_LIMITS = (5, SIM_DURATION / 1000)


def apply_exp_cfg(cfg):

    # Duration
    cfg.duration = SIM_DURATION

    # Populations to use
    pops_active = ['NGF1', 'NGF2', 'NGF3', 'NGF4', 'NGF5A', 'NGF5B', 'NGF6']

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {
        'pops_active': pops_active,   
        'conns_frozen': 'all',   # all inputs are surrogate, no recurrent connections
        'fpath_frozen_rates': str(dirpath_self / 'target_state_1.csv'),   # surrogate input
    }

    # Global wight multiplier
    cfg.wmult = 0.1

    # Turn off subConn
    cfg.addSubConn = 0

    # OU current input
    cfg.add_ou_current = 1
    cfg.ou_common = 0
    cfg.ou_noise_duration = cfg.duration
    cfg.ou_tau = 10

    # Cell mechanisms to modify
    with open(dirpath_self / 'mech_changes_1.json', 'r') as fid:
        cfg.mech_changes = json.load(fid)

    if 'plotRaster' in cfg.analysis:
        cfg.analysis['plotRaster']['include'] = pops_active
    if 'plotSpikeStats' in cfg.analysis:
        cfg.analysis['plotSpikeStats']['include'] = pops_active
    if 'plotTraces' in cfg.analysis:
        cfg.analysis['plotTraces']['include'] = pops_active
    
    # Time range for rate and CV calculation
    #cfg.analysis['plotSpikeStats']['timeRange'] = [cfg.duration - 1000, cfg.duration]
    cfg.analysis['plotSpikeStats'] = False

    # Record voltage traces
    ncells_rec = 4
    ncells_plot = 0
    cfg.recordCells = [(pop, list(range(ncells_rec))) for pop in pops_active]
    cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
    cfg.recordStep =  0.1
    if ncells_plot:
        cfg.analysis['plotTraces'] = {
            'include': [(pop, list(range(ncells_plot))) for pop in pops_active],
            'timeRange': [1000, cfg.duration],
            'oneFigPer': 'trace', 'overlay': False,
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

    # Base subfolder for the output saving
    exp_name_sub = gen_exp_name_sub()

    # Generate filename postfix with param values
    exp_id = exp_name.split('_')[-1]
    postfix = exp_id

    # Create subfolders to put the results
    dirpath_res = Path(cfg.saveFolder)
    dirpath_res_sub = dirpath_res / exp_name_sub
    os.makedirs(dirpath_res_sub, exist_ok=True)
    dirnames_sub = ['rasters', 'results', 'cfg']
    for dirname in dirnames_sub:
        os.makedirs(dirpath_res_sub / dirname, exist_ok=True)

    # Rename raster and move it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_raster.png'
    fpath_new = dirpath_res_sub / 'rasters' / f'raster_{postfix}.png'
    if fpath_old.exists():
        fpath_old.rename(fpath_new)

    # Rename config file and copy it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_cfg.json'
    fpath_new = dirpath_res_sub / 'cfg' / f'cfg_{postfix}.json'
    shutil.copy(fpath_old, fpath_new)

    # Save rates, CVs, and voltage stats to a json file
    t_limits = TCALC_LIMITS
    res = proc.calc_rates_and_cvs(sim, t_limits, nspikes_min=3)
    res |= proc.calc_v_stats(sim, t_limits, med_win=0.05)
    fpath_res = dirpath_res_sub / 'results' / f'result_{postfix}.json'
    with open(fpath_res, 'w') as fid:
        json.dump(res, fid, indent=4)
    
    """ # Rename traces file and move it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_traces.png'
    fpath_new = dirpath_res_sub / 'traces' / f'traces_{postfix}.png'
    if fpath_old.exists():
        fpath_old.rename(fpath_new) """
