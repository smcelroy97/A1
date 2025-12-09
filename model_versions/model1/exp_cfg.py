import json
from pathlib import Path
import sys

import warnings
warnings.filterwarnings("ignore")

dirpath_repo_root = Path(__file__).resolve().parents[3]
dirpath_self = Path(__file__).resolve().parent
sys.path.append(str(dirpath_repo_root))
sys.path.append(str(dirpath_self))

import pandas as pd


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

EE_FRAC_ACTIVE = 0.5

OU_INP_PATH = (
    'exp_results/single_i_ou_subnet_state1_mech1_nosub_wmult_0.25/'
    'full_model_split_ee_conn/exp_t_46.0_50.0_eefrac_0.5_kmu_0.1_ksigma_0.0_'
    'tau_200_taus_2500_tc0_2000_tlock_40000_kci_0.0005_kcp_0.0/ou_inputs_adj.json'
)

def apply_exp_cfg(cfg, par=None):

    conns_ee = [(pop1, pop2) for pop1 in POPS_E for pop2 in POPS_E]
    conns_ee = list(set(conns_ee))

    # Subnet parameters
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
    with open(dirpath_repo_root / OU_INP_PATH, 'r') as fid:
        cfg.ou_pop_inputs = json.load(fid)
    
    # Read target rates
    df = pd.read_csv(dirpath_self / 'target_state_1.csv')
    target_rates = df.set_index('pop_name')['target_rate'].to_dict()
    cfg.target_rates = target_rates

    # Cell mechanisms to modify
    with open(dirpath_self / 'mech_changes_1.json', 'r') as fid:
        cfg.mech_changes = json.load(fid)


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
