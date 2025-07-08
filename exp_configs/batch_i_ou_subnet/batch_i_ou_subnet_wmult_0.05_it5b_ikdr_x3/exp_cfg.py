import json
import os
from pathlib import Path


dirpath_self = Path(__file__).resolve().parent


def apply_exp_cfg(cfg):

    # Duration
    cfg.duration = 3 * 1e3

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {
        'pops_active': ['IT5B'],
        'conns_frozen': 'all',
        'fpath_frozen_rates': str(dirpath_self / 'frozen_rates.csv')
    }

    # Weight multiplier
    cfg.wmult = 0.05
    
    # OU current
    cfg.add_ou_current = 1
    cfg.ou_common = 0
    cfg.ou_noise_duration = cfg.duration
    cfg.ou_tau = 2
    # cfg.ou_pop_inputs will be filled in batch_params.post_update()

    # Time range for rate and CV calculation
    #cfg.analysis['plotRaster'] = False
    cfg.analysis['plotSpikeStats'] = False
    #cfg.analysis['plotSpikeStats']['timeRange'] = [3500, 5000]
    #cfg.analysis['plotSpikeStats']['timeRange'] = [2000, 3000]

    cfg.mech_changes = {
        'gkdr_all': {'pop': 'IT5B_reduced', 'sec': 'all',
                     'mech': 'kdr', 'par': 'gbar',
                     'mult': 3, 'add': 0}
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

    pop = 'IT5B'

    cfg = sim.cfg
    exp_name = cfg.simLabel

    # Generate filename postfix with param values
    exp_id = exp_name.split('_')[-1]
    postfix = (
        exp_id + f'_oumean_{cfg.ou_pop_inputs[pop]["ou_mean"] * 100 : .03f}'
    )

    # Create subfolders to put the results
    dirpath_res = Path(cfg.saveFolder)
    dirnames_sub = ['rasters', 'cfg', 'results']
    for dirname in dirnames_sub:
        os.makedirs(dirpath_res / dirname, exist_ok=True)

    # Rename raster and move it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_raster.png'
    fpath_new = dirpath_res / 'rasters' / f'raster_{postfix}.png'
    if fpath_old.exists():
        fpath_old.rename(fpath_new)

    # Rename cfg and move it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_cfg.json'
    fpath_new = dirpath_res / 'cfg' / f'cfg_{postfix}.json'
    fpath_old.rename(fpath_new)

    # Rename result file and move it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_result.json'
    fpath_new = dirpath_res / 'results' / f'result_{postfix}.json'
    fpath_old.rename(fpath_new)
