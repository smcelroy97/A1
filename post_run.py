import json
import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

import analysis.ou_tuning.netpyne_res_parse_utils as parse_utils
import analysis.ou_tuning.data_proc_utils as proc_utils


dirpath_self = Path(__file__).resolve().parent


def post_run(sim):
    """Called in the end of a job (after runnig and saving). """
    
    time_ranges = [(2.5, 3.5), (6, 7)]   # before and after the ramp

    cfg = sim.cfg

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

    for pop in ['IT5A']:
        
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
        fname_out = f'fi_curve_{pop}.png'
        plt.savefig(Path(cfg.saveFolder) / fname_out, dpi=300)
