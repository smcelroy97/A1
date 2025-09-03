import json
from pathlib import Path
import sys

dirpath_repo_root = Path(__file__).resolve().parents[3]
dirpath_self = Path(__file__).resolve().parent
sys.path.append(str(dirpath_repo_root))
#sys.path.append(str(dirpath_self))

from analysis.ou_tuning import sim_res_proc_utils as proc


def apply_exp_cfg(cfg):

    # Duration
    cfg.duration = 10 * 1e3

    # Populations to use
    pops_active = ['NGF1', 'NGF2', 'NGF3', 'NGF4', 'NGF5A', 'NGF5B', 'NGF6']

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {
        'pops_active': pops_active,   
        'conns_frozen': 'all',   # all inputs are surrogate, no recurrent connections
        'fpath_frozen_rates': str(dirpath_self / 'target_state_1.csv'),   # surrogate input
    }

    # Global weight multiplier
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

    if 'plotRaster' in cfg.analysis:
        cfg.analysis['plotRaster']['include'] = pops_active
    if 'plotSpikeStats' in cfg.analysis:
        cfg.analysis['plotSpikeStats']['include'] = pops_active
    if 'plotTraces' in cfg.analysis:
        cfg.analysis['plotTraces']['include'] = pops_active
    
    # Time range for rate and CV calculation
    cfg.analysis['plotSpikeStats']['timeRange'] = [5000, cfg.duration]
    #cfg.analysis['plotSpikeStats'] = False

    # Record voltage traces
    ncells_rec = 4
    ncells_plot = 2
    cfg.recordCells = [(pop, list(range(ncells_rec))) for pop in pops_active]
    cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
    cfg.recordStep =  0.1
    cfg.analysis['plotTraces'] = {
        'include': [(pop, list(range(ncells_plot))) for pop in cfg.allpops],
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

    # Calculate rate and CV for each pop., save the result to json
    t_limits = (5, cfg.duration / 1000)
    nspikes_min = 3
    res = proc.calc_rates_and_cvs(sim, t_limits, nspikes_min)
    fpath_res = '{}/{}_result.json'.format(cfg.saveFolder, cfg.simLabel)
    with open(fpath_res, 'w') as fid:
        json.dump(res, fid, indent=4)
