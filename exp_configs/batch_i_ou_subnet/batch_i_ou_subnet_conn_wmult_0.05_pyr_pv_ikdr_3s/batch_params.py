from pathlib import Path

import numpy as np
import pandas as pd


def generate_active_pop_groups() -> dict[str, list[str]]:
    """ pop_groups_cortex = {
        'L23': ['IT2', 'IT3', 'PV2', 'PV3'],
        'L4': ['ITP4', 'ITS4', 'PV4'],
        'L5A': ['IT5A', 'CT5A', 'PV5A'],
        'L5B': ['IT5B', 'CT5B' , 'PT5B', 'PV5B'],
        'L6': ['IT6', 'CT6', 'PV6']
    } """
    pop_groups_cortex = {
        'L2': ['IT2', 'PV2'],
        'L3': ['IT3', 'PV3'],
        'L4': ['ITP4', 'PV4'],
        'L4S': ['ITS4', 'PV4'],
        'L5A': ['IT5A', 'PV5A'],
        'L5B': ['IT5B', 'PV5B'],
        'L6': ['IT6', 'PV6']
    }
    pops_thal = ['TC', 'HTC', 'TI', 'IRE']
    pop_groups = {}
    for name, pops in pop_groups_cortex.items():
        pop_groups[name] = pops.copy()
        #pop_groups[f'{name}_thal'] = pops + pops_thal
    """ for name1, pops1 in pop_groups_cortex.items():
        for name2, pops2 in pop_groups_cortex.items():
            pop_groups[f'{name1}_{name2}'] = pops1 + pops2
            pop_groups[f'{name1}_{name2}_thal'] = pops1 + pops2 + pops_thal """
    return pop_groups


def get_batch_params():
    """Generate params for batchtools to probe. """
    pop_groups = generate_active_pop_groups()
    params = {
        'pop_group_active': list(pop_groups.keys())
    }
    return params


def post_update(cfg):
    """Called after cfg.update() """
    pop_groups = generate_active_pop_groups()
    group_name = cfg.pop_group_active
    cfg.subnet_params['pops_active'] = pop_groups[group_name]


if __name__ == '__main__':
    from pprint import pprint
    pop_groups = generate_active_pop_groups()
    for n, name in enumerate(pop_groups):
        print(f'{n} {name}: {" ".join(pop_groups[name])}')
