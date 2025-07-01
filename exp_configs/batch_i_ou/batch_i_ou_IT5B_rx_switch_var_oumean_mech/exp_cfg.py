import json
import os
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

dirpath_self = Path(__file__).resolve().parent
dirpath_repo_root = Path(__file__).resolve().parents[3]
sys.path.append(str(dirpath_repo_root))

import analysis.ou_tuning.netpyne_res_parse_utils as parse_utils
import analysis.ou_tuning.data_proc_utils as proc_utils


def apply_exp_cfg(cfg):
    """Applied after default cfg creation and before netParams creation. """

    # Duration
    cfg.duration = 7 * 1e3
    
    # Turn off the connections and bkg inputs
    cfg.addConn = 0
    cfg.addBkgConn = 0

    # Populations to use
    cfg.pops_active = [
        'IT5B'
    ]
    cfg.allpops = cfg.pops_active
    if 'plotRaster' in cfg.analysis:
        cfg.analysis['plotRaster']['include'] = cfg.pops_active
    if 'plotSpikeStats' in cfg.analysis:
        cfg.analysis['plotSpikeStats']['include'] = cfg.pops_active
    if 'plotTraces' in cfg.analysis:
        cfg.analysis['plotTraces']['include'] = cfg.pops_active
    
    cfg.analysis['plotSpikeStats'] = False
    
    # OU current
    cfg.add_ou_current = 1
    cfg.ou_common = 1    # all pops receive the same OU input
    cfg.ou_noise_duration = cfg.duration
    cfg.ou_tau = 2
    cfg.OUamp = [-0.02, 0.2]
    #cfg.OUamp = [-0.02, 0.07]
    cfg.oustd_lin = (0.002, 0.2)
    cfg.OUstd = [np.maximum(0, cfg.oustd_lin[0] + cfg.oustd_lin[1] * x)
                 for x in cfg.OUamp]

    # NetStim inputs
    cfg.bkg_spike_inputs = {
        'IT5B': {'r': 75, 'w': 0.5}
    }

    # Record voltage traces
    """ cells_rec = [0, 50, 100, 150, 200, 250, 300, 350, 400, 450]
    cfg.recordCells = [(pop, cells_rec) for pop in cfg.allpops]
    cfg.recordTraces = {
        'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'},
        #'p_kBK': {'sec': 'soma', 'loc': 0.5, 'var': 'p', 'mech': 'kBK'}
        #'n_kdr': {'sec': 'soma', 'loc': 0.5, 'var': 'n', 'mech': 'kdr'}
    }
    cfg.recordStep =  0.1
    cfg.analysis['plotTraces'] = {
        'include': [(pop, cells_rec) for pop in cfg.allpops],
        'timeRange': [0, cfg.duration],
        'oneFigPer': 'cell', 'overlay': False,
        'saveFig': True, 'showFig': False, 'figSize': (18, 12)
    } """

    # OU ramp
    #cfg.ou_ramp_dur = None
    cfg.ou_ramp_dur = 1000
    cfg.ou_ramp_t0 = 3500
    cfg.ou_ramp_offset = 1
    cfg.ou_ramp_mult = 0
    #cfg.ou_ramp_type = 'up_down'
    cfg.ou_ramp_type = 'up'


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
    'gnax_all': {'sec': 'all', 'mech': 'nax', 'par': 'gbar',
             'mult_vals': [0.1, 0.25, 0.5, 1]},
}


def modify_net_params(cfg, params):
    """Applied after netParams creation. """
    
    # Modify membrane currents
    v = var_mechs_info[cfg.mech_var]
    secs_all = params.cellParams['IT5B_reduced']['secs']
    if v['sec'] == 'all':
        secs = list(secs_all.values())
    else:
        secs = [secs_all[v['sec']]]
    mult = v['mult_vals'][cfg.mech_mult_num]
    for sec in secs:
        sec['mechs'][v['mech']][v['par']] *= mult

    # Add NetStim inputs
    pop = 'IT5B'
    params.stimSourceParams[f'bkg_src_{pop}'] = {
        'type': 'NetStim',
        #'start': 0,
        'rate': cfg.bkg_spike_inputs[pop]['r'],
        'noise': 1.0,
        #'number': 1e9
    }
    params.stimTargetParams[f'bkg_targ_{pop}'] =  {
        'source': f'bkg_src_{pop}',
        'conds': {'pop': pop},
        'sec': 'apic',
        'loc': 0.5,
        'synMech': 'AMPA',
        #'synMech': ['AMPA', 'NMDA'],
        'weight': cfg.bkg_spike_inputs[pop]['w'],
    }


def post_run(sim):
    """Called in the end of a job (after runnig and saving). """

    pop = 'IT5B'
    time_ranges = [(2.5, 3.5), (6, 7)]   # before and after the ramp

    cfg = sim.cfg
    exp_name = cfg.simLabel

    # Extract spike times from the sim result
    sim_result = parse_utils.prepare_sim_result(sim)
    spikes = parse_utils.get_pop_spikes(sim_result, pop, combine_cells=False)

    # Calculate pre- and post-ramp firing rates
    avg_rates = []
    for n, t_range in enumerate(time_ranges):
        rr = proc_utils.calc_pop_rate(spikes, t_range)
        avg_rates.append(rr)
    
    # OU amplitudes and std's corresponding to the neurons
    ncells = len(spikes)
    ouamp_min, ouamp_max = sim.cfg.OUamp
    ou_amps = np.linspace(ouamp_min, ouamp_max, ncells)
    ou_stds = np.maximum(0, cfg.oustd_lin[0] + cfg.oustd_lin[1] * ou_amps)
    
    # Plot pre- / post-ramp firing rate vs. OU amplitude
    plt.figure(figsize=(12, 6))
    for n, t_range in enumerate(time_ranges):
        plt.plot(ou_amps, np.array(avg_rates[n]) + n, '.',
                 label=f't=({t_range[0]}-{t_range[1]})')
    plt.xlabel('OU amplitude')
    plt.ylabel('Avg. rate (Hz)')
    plt.title(f'Pop: {pop}')
    plt.legend()

    # Generate filename postfix with param values
    mechs = sim.net.params.cellParams['IT5B_reduced']['secs']['soma'] ['mechs']
    bkg = cfg.bkg_spike_inputs[pop]
    exp_id = exp_name.split('_')[-1]
    mult = var_mechs_info[cfg.mech_var]['mult_vals'][cfg.mech_mult_num]
    postfix = (
        exp_id + 
        f'_oustd_{cfg.oustd_lin[0] * 100}_{cfg.oustd_lin[1]}'
        f'_ramp_{cfg.ou_ramp_offset:.02f}_{cfg.ou_ramp_mult}'
        f'_rx_{bkg["r"]}_wx_{bkg["w"]:.02f}'
        f'_{cfg.mech_var}_mult_{mult}'
    )

    # Create subfolders to put the results
    dirpath_res = Path(cfg.saveFolder)
    dirnames_sub = ['ir_avg', 'rasters', 'cfg', 'params', 'rates']
    for dirname in dirnames_sub:
        os.makedirs(dirpath_res / dirname, exist_ok=True)

    # Save the plot of pre- / post-ramp firing rate vs. OU amplitude
    fname_out = f'ir_avg_{postfix}.png'
    plt.savefig(dirpath_res / 'ir_avg' / fname_out, dpi=300)

    # Rename raster and move it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_raster.png'
    fpath_new = dirpath_res / 'rasters' / f'raster_{postfix}.png'
    fpath_old.rename(fpath_new)

    # Rename cfg and move it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_cfg.json'
    fpath_new = dirpath_res / 'cfg' / f'cfg_{postfix}.json'
    fpath_old.rename(fpath_new)

    # Rename params and move it to a subfolder
    fpath_old = dirpath_res / f'{exp_name}_params.json'
    fpath_new = dirpath_res / 'params' / f'params_{postfix}.json'
    fpath_old.rename(fpath_new)

    # Create and save xarray with avg. firing rates
    time_range_labels = [f't=({t[0]}-{t[1]})' for t in time_ranges]
    data = xr.DataArray(
        data=np.array(avg_rates), 
        dims=['interval', 'cell'], 
        coords={
            'interval': ['pre', 'post'],
            'time_range': ('interval', time_range_labels),
            'cell': np.arange(ncells),
            'ou_mean': ('cell', ou_amps),
            'ou_std': ('cell', ou_stds)
        }
    )
    data.attrs = {
        'oustd_lin_c': cfg.oustd_lin[0],
        'oustd_lin_k': cfg.oustd_lin[1],
        'ramp_offset': cfg.ou_ramp_offset,
        'ramp_mult':  cfg.ou_ramp_mult,
        'rx': bkg['r'],
        'wx': bkg['w']
    }
    fname_out = f'rates_{postfix}.nc'
    data.to_netcdf(dirpath_res / 'rates' / fname_out)
