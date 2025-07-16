import json
import os
from pathlib import Path
import shutil


dirpath_self = Path(__file__).resolve().parent

""" pop_groups = {
    pop: [pop] for pop in [
        'IT2', 'PV2', 'IT3', 'PV3', 'ITP4', 'ITS4', 'PV4',
        'IT5A', 'PV5A', 'IT5B', 'PV5B', 'IT6', 'PV6',
    ]
}
pop_groups |= {
    'L2': ['IT2', 'PV2'],
    'L3': ['IT3', 'PV3'],
    'L4P': ['ITP4', 'PV4'],
    'L4S': ['ITS4', 'PV4'],
    'L5A': ['IT5A', 'PV5A'],
    'L5B': ['IT5B', 'PV5B'],
    'L6': ['IT6', 'PV6'],
    'L6pyr': ['IT6', 'CT6', 'PV6'],
    'L23': ['IT2', 'IT3', 'PV2', 'PV3'],
    'L4': ['ITP4', 'ITS4', 'PV4'],
} """

pop_groups = {'IT2': ['IT2'], 'ITP4': ['ITP4']}


def apply_exp_cfg(cfg, par):

    print(pop_groups)
    print(f'>>>> {par}')

    group_name, ramp = par.split(' ')
    cfg.pop_group_active = group_name
    ramp = int(ramp)
    print(f'Group: {cfg.pop_group_active}')
    print(f'Ramp: {ramp}')

    # Duration
    cfg.duration = 10 * 1e3

    # Subnet parameters
    cfg.subnet_build_flag = 1
    cfg.subnet_params = {
        'pops_active': pop_groups[group_name],   
        'conns_frozen': [],
        #'conns_frozen': 'all',
        'fpath_frozen_rates': str(dirpath_self / 'frozen_rates.csv'),
        #'duplicate_active_pops': 1
    }

    # Weight multiplier
    cfg.wmult = 0.05

    # OU current
    cfg.add_ou_current = 1
    cfg.ou_common = 0
    cfg.ou_noise_duration = cfg.duration
    cfg.ou_tau = 2
    with open(dirpath_self / 'ou_inputs.json', 'r') as fid:
        cfg.ou_pop_inputs = json.load(fid)

    # Time range for rate and CV calculation
    #cfg.analysis['plotSpikeStats']['timeRange'] = [3500, 5000]
    #cfg.analysis['plotSpikeStats']['timeRange'] = [cfg.duration - 1000, cfg.duration]
    cfg.analysis['plotSpikeStats'] = False

    gkdr_mults = {'IT2': 1.5, 'IT3': 1.5, 'ITP4': 3, 'IT5A': 3, 'IT5B': 3,
                  'CT5A': 3, 'CT5B': 3, 'IT6': 3, 'CT6': 3}
    cfg.mech_changes = {}
    for pop, mult in gkdr_mults.items():
        cfg.mech_changes[f'gkdr_{pop}'] = {
            'pop': f'{pop}_reduced', 'sec': 'all',
            'mech': 'kdr', 'par': 'gbar',
            'mult': mult, 'add': 0
        }
    
    # Initial OU ramp
    cfg.ou_ramp_dur = 1000
    cfg.ou_ramp_offset = ramp
    cfg.ou_ramp_mult = 1

    # Experiment subname
    exp_name_sub = '100'
    if cfg.subnet_params['conns_frozen'] == 'all':
        exp_name_sub += '_unconn'
    if cfg.ou_ramp_offset == 0:
        exp_name_sub += '_noramp'
    else:
        exp_name_sub += '_ramp'
    exp_name_sub += f'_{int(cfg.duration / 1000)}s'
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

    # Generate filename postfix with param values
    exp_id = exp_name.split('_')[-1]
    postfix = f'{exp_id}_{cfg.pop_group_active}'

    # Create subfolders to put the results
    dirpath_res = Path(cfg.saveFolder)
    dirpath_res_sub = dirpath_res / cfg.exp_name_sub
    os.makedirs(dirpath_res_sub, exist_ok=True)
    dirnames_sub = ['rasters', 'results', 'cfg']
    for dirname in dirnames_sub:
        os.makedirs(dirpath_res_sub / dirname, exist_ok=True)

    # Rename raster and move it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_raster.png'
    fpath_new = dirpath_res_sub / 'rasters' / f'raster_{postfix}.png'
    if fpath_old.exists():
        fpath_old.rename(fpath_new)

    # Rename result file and move it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_result.json'
    fpath_new = dirpath_res_sub / 'results' / f'result_{postfix}.json'
    fpath_old.rename(fpath_new)

    # Rename config file and copy it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_cfg.json'
    fpath_new = dirpath_res_sub / 'cfg' / f'cfg_{postfix}.json'
    shutil.copy(fpath_old, fpath_new)
