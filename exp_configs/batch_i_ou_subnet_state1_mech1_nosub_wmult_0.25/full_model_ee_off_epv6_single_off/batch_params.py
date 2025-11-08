
pops_active = [
    'NGF1',
    'IT2', 'PV2', 'SOM2', 'VIP2', 'NGF2',
    'IT3', 'PV3', 'SOM3', 'VIP3', 'NGF3',
    'ITP4', 'ITS4', 'PV4', 'SOM4', 'VIP4', 'NGF4',
    'IT5A', 'CT5A', 'PV5A', 'SOM5A', 'VIP5A', 'NGF5A',
    'IT5B', 'CT5B' , 'PT5B', 'PV5B', 'SOM5B', 'VIP5B', 'NGF5B',
    'IT6', 'CT6', 'PV6', 'SOM6', 'VIP6', 'NGF6',
    'TC', 'TCM', 'HTC', 'TI', 'TIM', 'IRE', 'IREM'
]

pops_e = ['IT2', 'IT3', 'ITS4', 'ITP4', 'IT5A', 'CT5A',
          'IT5B', 'CT5B', 'PT5B', 'IT6', 'CT6']

frozen_conn_pop_post = 'PV6'


def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'frozen_conn_pop_pre': pops_e
    }
    return params


def post_update(cfg):
    """Called after cfg.update() """

    # Turn off conns between excitatory pops
    pops_e_active = [pop for pop in pops_e if pop in pops_active]
    conns_ee = [(pop1, pop2) for pop1 in pops_e_active for pop2 in pops_e_active]
    conns_ee = list(set(conns_ee))  # remove duplicates
    cfg.subnet_params['conns_frozen'] = conns_ee

    # Turn off conn between frozen_conn_pop_pre and frozen_conn_pop_post
    cfg.subnet_params['conns_frozen'] += [(cfg.frozen_conn_pop_pre, frozen_conn_pop_post)]
