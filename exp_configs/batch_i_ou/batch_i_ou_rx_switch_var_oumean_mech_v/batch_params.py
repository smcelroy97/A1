import json
from pathlib import Path

import numpy as np
import pandas as pd


var_mechs_info = {
    'gkdr': {'sec': 'soma', 'mech': 'kdr', 'par': 'gbar',
             'mult_vals': [1, 2, 3, 4]},
    'gnax': {'sec': 'soma', 'mech': 'nax', 'par': 'gbar',
             'mult_vals': [0.1, 0.25, 0.5, 1]},
    'tau_cadad': {'sec': 'soma', 'mech': 'cadad', 'par': 'taur',
                  'mult_vals': [0.25, 0.5, 0.75, 1]},
    'tau_kbk': {'sec': 'soma', 'mech': 'kBK', 'par': 'tau',
                'mult_vals': [1, 25, 50, 100]},
    'gcal': {'sec': 'soma', 'mech': 'cal', 'par': 'gcalbar',
             'mult_vals': [0.25, 0.5, 0.75, 1]},
    'gcan': {'sec': 'soma', 'mech': 'can', 'par': 'gcanbar',
             'mult_vals': [0.25, 0.5, 0.75, 1]},
    'gcat': {'sec': 'soma', 'mech': 'cat', 'par': 'gcatbar',
             'mult_vals': [0.25, 0.5, 0.75, 1]},
    'gkdr_all': {'sec': 'all', 'mech': 'kdr', 'par': 'gbar',
                 'mult_vals': [1, 2, 3, 4]},
                 #'mult_vals': [2.25, 2.5, 2.75, 3]},
    'gnax_all': {'sec': 'all', 'mech': 'nax', 'par': 'gbar',
                 'mult_vals': [0.1, 0.25, 0.5, 1]},
}

def get_batch_params():
    """Generate params for batchtools to probe. """

    # Save var_mechs_info as a JSON file
    fpath_json = Path(__file__).resolve().parent / 'var_mechs_info.json'
    with open(fpath_json, 'w') as fid:
        json.dump(var_mechs_info, fid, indent=4)

    params = {
        'ou_ramp_offset': [0.75, 1.5, 2, 3, 4],
        #'bkg_r': [75, 100, 150, 200],
        #'bkg_w': [0.25, 0.5, 0.75, 1],
        'bkg_r': [75],
        'bkg_w': [0.5],
        'mech_var': ['gkdr_all'],
        #'mech_mult_num': [0, 1, 2, 3]
        'mech_mult_num': [0, 1, 2]
    }
    return params


def post_update(cfg):
    """Called after cfg.update() """
    cfg.bkg_spike_inputs = {pop: {'r': cfg.bkg_r, 'w': cfg.bkg_w}
                            for pop in cfg.pops_active}


""" if __name__ == '__main__':
    from pprint import pprint
    pop_groups = generate_active_pop_groups()
    for n, name in enumerate(pop_groups):
        print(f'{n} {name}: {" ".join(pop_groups[name])}') """
