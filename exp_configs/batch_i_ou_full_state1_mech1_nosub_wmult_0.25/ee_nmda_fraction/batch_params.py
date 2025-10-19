#import numpy as np


def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'k_nmda_ee': [0.5, 0.625, 0.75, 0.875, 1]
    }
    return params


def post_update(cfg):
    """Called after cfg.update() """

    # AMPA:NMDA ratio
    cfg.synWeightFractionEE = [1 - cfg.k_nmda_ee, cfg.k_nmda_ee]

