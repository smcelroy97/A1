
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

frozen_conn_groups = {
    'IT3': [('IT3', 'IT3')],
    'SELF': [(pop, pop) for pop in pops_e],
    'ALL': [(pop1, pop2) for pop1 in pops_e for pop2 in pops_e]
}


def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'frozen_conn_group': list(frozen_conn_groups.keys())
    }
    return params


def post_update(cfg):
    """Called after cfg.update() """

    # Set active pops of the subnet (others are surrogate)
    cfg.subnet_params['pops_active'] = pops_active

    # Turn off conns between pops
    cfg.subnet_params['conns_frozen'] = (
        frozen_conn_groups[cfg.frozen_conn_group])

    if 'plotRaster' in cfg.analysis:
        cfg.analysis['plotRaster']['include'] = pops_active
    if 'plotSpikeStats' in cfg.analysis:
        cfg.analysis['plotSpikeStats']['include'] = pops_active
    if 'plotTraces' in cfg.analysis:
        cfg.analysis['plotTraces']['include'] = pops_active
    
    # Record voltage traces
    ncells_rec = 4
    ncells_plot = 1
    cfg.recordCells = [(pop, list(range(ncells_rec))) for pop in pops_active]
    cfg.recordTraces = {'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}}
    cfg.recordStep =  0.1
    cfg.analysis['plotTraces'] = {
        'include': [(pop, list(range(ncells_plot))) for pop in pops_active],
        'timeRange': [1000, cfg.duration],
        'oneFigPer': 'cell', 'overlay': False,
        'saveFig': True, 'showFig': False, 'figSize': (18, 12)
    }
