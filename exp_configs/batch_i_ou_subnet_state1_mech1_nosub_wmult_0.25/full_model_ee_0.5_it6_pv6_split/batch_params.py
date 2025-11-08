#import numpy as np

CONN_FRAC_ACTIVE_VALS = [0, 0.25, 0.5, 0.75, 1]
#CONN_FRAC_ACTIVE_VALS = [0.6, 0.7, 0.8, 0.9, 1]


def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'conn_frac_active': CONN_FRAC_ACTIVE_VALS
    }
    return params


def post_update(cfg):
    """Called after cfg.update() """

    # Split the connection
    cfg.subnet_params['conns_split']['IT6, PV6'] = cfg.conn_frac_active
