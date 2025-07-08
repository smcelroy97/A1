import json
import os
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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
    
    # Turn off the connections
    cfg.addConn = 0

    # Turn on/off bkg inputs
    cfg.addBkgConn = 1

    cfg.pop_main = 'IT3'

    # Populations to use
    cfg.pops_active = [cfg.pop_main]
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
    cfg.OUamp = [-0.02, 0.1]
    cfg.oustd_lin = (0.002, 0.2)
    cfg.OUstd = [np.maximum(0, cfg.oustd_lin[0] + cfg.oustd_lin[1] * x)
                 for x in cfg.OUamp]

    # NetStim inputs
    cfg.bkg_r = 200
    cfg.bkg_w = 2
    cfg.bkg_spike_inputs = {pop: {'r': cfg.bkg_r, 'w': cfg.bkg_w}
                            for pop in cfg.pops_active}
    
    # Load a table of pop sizes
    fpath_csv = dirpath_self / 'pops_sz.csv'
    pops_sz_df = pd.read_csv(fpath_csv)
    pops_sz = pops_sz_df.set_index('pop')['ncells'].to_dict()

    # Choose the cells to record voltages for each active pop.
    ncells_rec = 15
    cfg.pop_cells_rec = {}
    for pop in cfg.allpops:
        N = np.minimum(pops_sz[pop], ncells_rec)
        cfg.pop_cells_rec[pop] = np.linspace(0, pops_sz[pop] - 1, N, dtype=int)

    # Record voltage traces
    cfg.recordCells = [(pop, list(cfg.pop_cells_rec[pop]))
                       for pop in cfg.allpops]
    cfg.recordTraces = {
        'V_soma': {'sec': 'soma', 'loc': 0.5, 'var': 'v'}
    }
    cfg.recordStep =  0.1
    """ cfg.analysis['plotTraces'] = {
        'include': cfg.recordCells,
        'timeRange': [0, cfg.duration],
        'oneFigPer': 'cell', 'overlay': False,
        'saveFig': True, 'showFig': False, 'figSize': (18, 12)
    } """

    # OU ramp
    #cfg.ou_ramp_dur = None
    cfg.ou_ramp_dur = 1000
    cfg.ou_ramp_t0 = 3500
    cfg.ou_ramp_offset = 1.5
    cfg.ou_ramp_mult = 0
    cfg.ou_ramp_type = 'up'

    cfg.gkdr_mult = 1.5
    cfg.mech_changes = {}
    for pop in cfg.pops_active:
        cfg.mech_changes[f'gkdr_{pop}'] = {
            'pop': f'{pop}_reduced', 'sec': 'all',
            'mech': 'kdr', 'par': 'gbar',
            'mult': cfg.gkdr_mult, 'add': 0
        }


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

    # Add NetStim inputs
    for pop in cfg.pops_active:
        params.stimSourceParams[f'bkg_src_{pop}'] = {
            'type': 'NetStim',
            'rate': cfg.bkg_spike_inputs[pop]['r'],
            'noise': 1.0,
        }
        params.stimTargetParams[f'bkg_targ_{pop}'] =  {
            'source': f'bkg_src_{pop}',
            'conds': {'pop': pop},
            'sec': 'apic',
            'loc': 0.5,
            'synMech': 'AMPA',
            'weight': cfg.bkg_spike_inputs[pop]['w']
        }


def post_run(sim):
    """Called in the end of a job (after runnig and saving). """

    time_ranges = [(2.5, 3.5), (6, 7)]   # before and after the ramp

    cfg = sim.cfg
    exp_name = cfg.simLabel

    # Create subfolders to put the results
    dirpath_res = Path(cfg.saveFolder)
    dirnames_sub = ['ir_avg', 'rasters', 'cfg', 'params', 'rates',
                    'vstats', 'vtraces']
    for dirname in dirnames_sub:
        os.makedirs(dirpath_res / dirname, exist_ok=True)
    
    # Generate filename postfix with param values
    pop = cfg.pop_main
    postfix = (
        f'{pop}_bkg_{int(cfg.addBkgConn)}'
        f'_ramp_{cfg.ou_ramp_offset:.02f}_{cfg.ou_ramp_mult}'
        f'_rx_{cfg.bkg_r}_wx_{cfg.bkg_w:.02f}'
        f'_gkdr_mult_{cfg.gkdr_mult}'
        f'_oustd_{cfg.oustd_lin[0] * 100}_{cfg.oustd_lin[1]}'
    )

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

    # Collect sim result
    sim_result = parse_utils.prepare_sim_result(sim)

    # Extract voltages
    V0, tt = [], []
    for t_limits in time_ranges:
        V_, tt_ = parse_utils.get_voltages(
            sim_result, np.array(t_limits) * 1000
        )
        V0.append(V_)
        tt.append(tt_)

    # Extract spike times from the sim result
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
    plt.figure(111, figsize=(12, 6))
    plt.clf()
    for n, t_range in enumerate(time_ranges):
        plt.plot(ou_amps, np.array(avg_rates[n]) + n, '.',
                label=f't=({t_range[0]}-{t_range[1]})')
    plt.xlabel('OU amplitude')
    plt.ylabel('Avg. rate (Hz)')
    plt.title(f'Pop: {pop}')
    plt.legend()

    # Save the plot of pre- / post-ramp firing rate vs. OU amplitude
    fname_out = f'ir_avg_{postfix}.png'
    plt.savefig(dirpath_res / 'ir_avg' / fname_out, dpi=300)

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
        'rx': cfg.bkg_r,
        'wx': cfg.bkg_w
    }
    fname_out = f'rates_{postfix}.nc'
    data.to_netcdf(dirpath_res / 'rates' / fname_out)

    # Create and save xarray with voltages
    V = [V0_[pop] for V0_ in V0]
    cell_idx = cfg.pop_cells_rec[pop]
    V_data = xr.DataArray(
        data=V, 
        dims=['interval', 'cell', 'time'], 
        coords={
            'interval': ['pre', 'post'],
            'time_range': ('interval', time_range_labels),
            'cell': cell_idx,
            'ou_mean': ('cell', ou_amps[cell_idx]),
            'ou_std': ('cell', ou_stds[cell_idx]),
            'time': tt[0] / 1000
        }
    )
    V_data.attrs = data.attrs

    # Create and save xarray with voltage statistics
    V_stats = xr.Dataset({
        'vmin': V_data.min(dim='time'),
        'vmax': V_data.max(dim='time'),
        'vmed': V_data.median(dim='time'),
        'vavg': V_data.mean(dim='time')
    })
    V_stats.attrs = V_data.attrs
    fname_out = f'vstats_{postfix}.nc'
    V_stats.to_netcdf(dirpath_res / 'vstats' / fname_out)
