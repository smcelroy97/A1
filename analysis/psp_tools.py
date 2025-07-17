import pickle
import os
import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import csv
from mpi4py import MPI
import pickle

batch_dir = '../simOutput/PSPTest/'

comm = MPI.COMM_WORLD
rank = comm.Get_rank()

files = [f for f in os.listdir(batch_dir) if f.endswith('.pkl')]
files.sort()  # Ensure consistent order

# Distribute files among ranks
my_files = files[rank::comm.Get_size()]

save_csv = 1
plot_psp_secs = 0
plot_avg_vs_secs = 1
plot_psp_matrix = 0
plot_psp_box = 0

with open('../conn/conn.pkl', 'rb') as f:
    conn_data = pickle.load(f)

wmat = conn_data['wmat']

pop_psps = {}
psp_amps = {}


for file in my_files:
    with open(batch_dir + file, 'rb') as f:
        print(f'Loading {file}...')
        sim_results = pickle.load(f)

    prePop = sim_results['simConfig']['prePop']

    # Extract pop, cell type, and sections
    for pop in sim_results['net']['params']['popParams']:
        if '_stim' in pop:
            continue
        pop_psps[pop] = {}
        pop_psps[pop][prePop] = {}
        if prePop in sim_results['simConfig']['Epops'] + sim_results['simConfig']['TEpops']:
            pop_psps[pop][prePop]['syn_type'] = 'E'
        else:
            pop_psps[pop][prePop]['syn_type'] = 'I'

        pop_psps[pop][prePop]['secs'] = {}

        # Get the section specific delays
        for conn in sim_results['net']['params']['connParams'].values():
            if pop == conn['postConds']['pop']:
                pop_psps[pop][prePop]['secs'][conn['sec']] = {}
                pop_psps[pop][prePop]['secs'][conn['sec']]['delay'] = conn['delay']

        # Extract gid for pop (for single cell batch)
        for cell in sim_results['net']['cells']:
            if cell['tags']['pop'] == pop:
                pop_psps[pop][prePop]['gid'] = cell['gid']
                break

        baseline_ms = 50  # ms before stim
        post_stim_ms = 500  # ms after stim to look for PSP
        dt = sim_results['simConfig']['dt']
        sec_amps = []

        baseline_window = int(baseline_ms / dt)
        post_window = int(post_stim_ms / dt)

        for sec in pop_psps[pop][prePop]['secs'].values():
            stim_idx = int(sec['delay'] / dt)
            trace = sim_results['simData']['V_soma']['cell_' + str(pop_psps[pop][prePop]['gid'])]
            # Indices for baseline and post-stimulus
            start_baseline = max(0, stim_idx - baseline_window)
            end_baseline = stim_idx
            start_post = stim_idx
            end_post = min(len(trace), stim_idx + post_window)
            # Store the trace window (baseline + post)
            sec['trace'] = trace[start_baseline:end_post]
            # Baseline from pre-stimulus
            baseline_mv = np.mean(trace[start_baseline:end_baseline])
            # Amplitude: largest signed deviation in post-stimulus window
            post_trace = trace[start_post:end_post]
            max_dev = np.max(post_trace - baseline_mv)
            min_dev = np.min(post_trace - baseline_mv)
            amplitude = max_dev if abs(max_dev) >= abs(min_dev) else min_dev
            sec['psp'] = amplitude
            sec_amps.append(amplitude)
        pop_psps[pop][prePop]['secs']['mean'] = np.mean(sec_amps)
        pop_psps[pop][prePop]['wmat_val'] = wmat[prePop][pop]


if plot_psp_secs:
    # Set up plotting for all sec traces and psps
    print('Plotting individual section traces...')
    for pop, prePop_dict in pop_psps.items():
        for prePop, data in prePop_dict.items():
            pop_dir = os.path.join(batch_dir, f'plots/{pop}_plots/{prePop}->{pop}')
            os.makedirs(pop_dir, exist_ok=True)
            traces = []
            times = None
            for sec_name, sec_data in data['secs'].items():
                if sec_name == 'mean':
                    continue
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
    print('Plotting average trace and section traces...')
    for pop, prePop_dict in pop_psps.items():
        for prePop, data in prePop_dict.items():
            pop_dir = os.path.join(batch_dir, f'plots/{pop}_plots/{prePop}->{pop}')
            os.makedirs(pop_dir, exist_ok=True)
            traces = []
            times = None
            for sec_name, sec_data in data['secs'].items():
                if sec_name == 'mean':
                    continue
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
    print('Plotting psp box plot')
    for pop, prePop_dict in pop_psps.items():
        for prePop, data in prePop_dict.items():
            pop_dir = os.path.join(batch_dir, f'plots/{pop}_plots/{prePop}->{pop}')
            os.makedirs(pop_dir, exist_ok=True)

            if len(data['secs']) > 1:
                plt.figure()
                plt.boxplot(list(psp_amps[pop].values()))
                plt.title('PSP Amplitudes Across Sections')
                plt.ylabel('Amplitude (mV)')
                # plt.savefig(os.path.join(pop_dir, f'psp_amplitudes_summary.png'))
                plt.close()


def strip_traces(d):
    for pop in d:
        for prePop in d[pop]:
            for sec in d[pop][prePop]['secs']:
                if sec != 'mean':
                    if 'trace' in d[pop][prePop]['secs'][sec]:
                        del d[pop][prePop]['secs'][sec]['trace']


strip_traces(pop_psps)

# Gather all pop_psps dicts to rank 0
all_pop_psps = comm.gather(pop_psps, root=0)

if save_csv and rank == 0:
    print('Exporting csv data to .csv...')
    # Merge all dictionaries
    merged_pop_psps = {}
    for d in all_pop_psps:
        for pop, prePop_dict in d.items():
            if pop not in merged_pop_psps:
                merged_pop_psps[pop] = {}
            merged_pop_psps[pop].update(prePop_dict)

    with open(f'{batch_dir}pop_psps.csv', 'w', newline='') as csvfile:
        fieldnames = ['pop', 'prePop', 'syn_type', 'psp', 'wmat_val']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for pop, prePop_dict in merged_pop_psps.items():  # <-- use merged_pop_psps here
            for prePop, data in prePop_dict.items():
                gid = data.get('gid', None)
                writer.writerow({
                    'pop': pop,
                    'prePop': prePop,
                    'syn_type': data['syn_type'],
                    'psp': data['secs']['mean'],
                    'wmat_val': data['wmat_val']
                })
