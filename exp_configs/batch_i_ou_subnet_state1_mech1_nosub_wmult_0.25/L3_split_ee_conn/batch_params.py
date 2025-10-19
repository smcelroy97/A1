#import numpy as np

#EE_FRAC_ACTIVE_VALS = [0, 0.25, 0.5, 0.75, 1]
EE_FRAC_ACTIVE_VALS = [0.6, 0.7, 0.8, 0.9, 1]


def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'ee_frac_active': EE_FRAC_ACTIVE_VALS
    }
    return params


def post_update(cfg):
    """Called after cfg.update() """

    # Split the connection
    cfg.subnet_params['conns_split']['IT3, IT3'] = cfg.ee_frac_active
