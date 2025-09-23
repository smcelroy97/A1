import json
import os
from pathlib import Path
import shutil
import sys

dirpath_repo_root = Path(__file__).resolve().parents[3]
dirpath_self = Path(__file__).resolve().parent
sys.path.append(str(dirpath_repo_root))
sys.path.append(str(dirpath_self))

#import numpy as np

#from analysis.ou_tuning import sim_res_proc_utils as proc


def apply_exp_cfg(cfg):

    # Duration
    cfg.duration = 10 * 1e3

    # Global weight multiplier
    cfg.wmult = 0.1

    # Turn off subConn
    cfg.addSubConn = 0

    # OU current input
    cfg.add_ou_current = 1
    cfg.ou_common = 0   # per-pop. inputs will be taken from a SimManager request
    cfg.ou_noise_duration = cfg.duration
    cfg.ou_tau = 10

    # Cell mechanisms to modify
    with open(dirpath_self / 'mech_changes_1.json', 'r') as fid:
        cfg.mech_changes = json.load(fid)
    
    # Time range for rate and CV calculation
    cfg.analysis['plotSpikeStats'] = False

    # To receive sim_label and request file path from batchtools
    cfg.sim_manager = {}


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

    pass
