
pop_groups = {
    'L2': ['IT2', 'PV2', 'SOM2', 'VIP2'],
    'L3': ['IT3', 'PV3', 'SOM3', 'VIP3'],
    'L4': ['ITP4', 'ITS4', 'PV4', 'SOM4', 'VIP4'],
    'L5A': ['IT5A', 'CT5A', 'PV5A', 'SOM5A', 'VIP5A'],
    'L5B': ['IT5B', 'CT5B' , 'PT5B', 'PV5B', 'SOM5B', 'VIP5B'],
    'L6': ['IT6', 'CT6', 'PV6', 'SOM6', 'VIP6']
}


def get_batch_params():
    """Generate params for batchtools to probe. """
    params = {
        'pop_group_active': list(pop_groups.keys())
    }
    return params


def post_update(cfg):
    """Called after cfg.update() """

    # Set active pops of the subnet (others are surrogate)
    group_name = cfg.pop_group_active
    pops_active = pop_groups[group_name]
    cfg.subnet_params['pops_active'] = pops_active

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

