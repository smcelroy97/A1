import pickle
import os
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import csv
from mpi4py import MPI

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

save_csv = 1
plot_psp_secs = 0
plot_avg_vs_secs = 0
plot_psp_matrix = 0
plot_psp_box = 0

batch_dir = '../simOutput/PSPTest/'

pop_psps = {}
psp_amps = {}

for file in os.listdir(batch_dir):
    if file.endswith('.pkl'):
        with open(batch_dir + file, 'rb') as f:
            sim_results = pickle.load(f)

        prePop = sim_results['simConfig']['prePop']
        # Extract pop, cell type, and sections
        for pop in sim_results['net']['params']['popParams']:
            if '_stim' in pop:
                continue
            pop_psps[pop] = {}
            pop_psps[pop][prePop + '_' + pop] = {}
            pop_psps[pop][prePop + '_' + pop]['secs'] = {}

            # Get the section specific delays
            for conn in sim_results['net']['params']['connParams'].values():
                if pop == conn['postConds']['pop']:
                    pop_psps[pop][prePop + '_' + pop]['secs'][conn['sec']] = {}
                    pop_psps[pop][prePop + '_' + pop]['secs'][conn['sec']]['delay'] = conn['delay']

            # Extract gid for pop (for single cell batch)
            for cell in sim_results['net']['cells']:
                if cell['tags']['pop'] == pop:
                    pop_psps[pop][prePop + '_' + pop]['gid'] = cell['gid']
                    break

            # Based on the section delay, extract the slice of the somatic trace
            baseline = 50
            post_stim = 1500  # ms after stimulus
            for sec in pop_psps[pop][prePop + '_' + pop]['secs'].values():
                post_window = int(post_stim / sim_results['simConfig']['dt'])
                baseline_window = int(post_stim / sim_results['simConfig']['dt'])
                stim_idx = int(sec['delay'] / sim_results['simConfig']['dt'])
                start = stim_idx - baseline_window
                end = stim_idx + post_window
                trace = sim_results['simData']['V_soma']['cell_' + str(pop_psps[pop][prePop + '_' + pop]['gid'])]
                sec['trace'] = trace[start:end]

                baseline_mv = np.mean(trace[:baseline_window])
                if prePop in sim_results['simConfig']['Epops'] + sim_results['simConfig']['TEpops']:
                    peak = np.max(trace[baseline_window:])
                else:
                    peak = np.min(trace[baseline_window:])
                amplitude = peak - baseline
                sec['psp'] = amplitude

# Gather all pop_psps dicts to rank 0
all_pop_psps = comm.gather(pop_psps, root=0)

if save_csv and rank == 0:
    # Merge all dictionaries
    merged_pop_psps = {}
    for d in all_pop_psps:
        for pop, prePop_dict in d.items():
            if pop not in merged_pop_psps:
                merged_pop_psps[pop] = {}
            merged_pop_psps[pop].update(prePop_dict)

    with open(f'{batch_dir}pop_psps.csv', 'w', newline='') as csvfile:
        fieldnames = ['pop', 'prePop', 'sec', 'delay', 'gid', 'psp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for pop, prePop_dict in pop_psps.items():
            for prePop_pop, data in prePop_dict.items():
                gid = data.get('gid', None)
                for sec, sec_data in data['secs'].items():
                    writer.writerow({
                        'pop': pop,
                        'prePop': prePop_pop,
                        'sec': sec,
                        'delay': sec_data.get('delay', None),
                        'gid': gid,
                        'psp': sec_data.get('psp', None)
                    })

if plot_psp_secs:
    # Set up plotting for all sec traces and psps
    for pop, prePop_dict in pop_psps.items():
        for prePop_pop, data in prePop_dict.items():
            pop_dir = os.path.join(batch_dir, f'plots/{pop}_plots/{prePop}->{pop}')
            os.makedirs(pop_dir, exist_ok=True)
            traces = []
            times = None
            for sec_name, sec_data in data['secs'].items():
                trace = sec_data['trace']
                dt = sim_results['simConfig']['dt']
                if times is None:
                    times = np.arange(len(trace)) * dt

                # Individual sec traces
                plt.figure()
                plt.plot(times, trace)
                plt.title(f'{prePop} -> {pop}: {sec_name}')
                plt.xlabel('Time (ms)')
                plt.ylabel('V (mV)')
                plt.savefig(os.path.join(pop_dir, f'{sec_name}_trace.png'))
                plt.close()

if plot_avg_vs_secs:
    for pop, prePop_dict in pop_psps.items():
        for prePop_pop, data in prePop_dict.items():
            pop_dir = os.path.join(batch_dir, f'plots/{pop}_plots/{prePop}->{pop}')
            os.makedirs(pop_dir, exist_ok=True)
            traces = []
            times = None
            for sec_name, sec_data in data['secs'].items():
                trace = sec_data['trace']
                dt = sim_results['simConfig']['dt']
                if times is None:
                    times = np.arange(len(trace)) * dt
                traces.append(trace)
            min_len = min(len(t) for t in traces)
            traces = [t[:min_len] for t in traces]
            times_avg = times[:min_len]
            plt.figure()
            for trace_window in traces:
                plt.plot(times_avg, trace_window, color='gray', alpha=0.5)
            avg_trace = np.mean(traces, axis=0)
            plt.plot(times_avg, avg_trace, color='red', label='Average')
            plt.title(f'All Traces and Average: {pop}')
            plt.xlabel('Time (ms)')
            plt.ylabel('V (mV)')
            plt.legend()
            plt.savefig(os.path.join(pop_dir, 'all_traces_with_average.png'))
            plt.close()

if plot_psp_box:
    for pop, prePop_dict in pop_psps.items():
        for prePop_pop, data in prePop_dict.items():
            pop_dir = os.path.join(batch_dir, f'plots/{pop}_plots/{prePop}->{pop}')
            os.makedirs(pop_dir, exist_ok=True)

            if len(data['secs']) > 1:
                plt.figure()
                plt.boxplot(list(psp_amps[pop].values()))
                plt.title('PSP Amplitudes Across Sections')
                plt.ylabel('Amplitude (mV)')
                # plt.savefig(os.path.join(pop_dir, f'psp_amplitudes_summary.png'))
                plt.close()
