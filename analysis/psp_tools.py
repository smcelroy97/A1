import pickle
import os
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

batch_dir = '../simOutput/PSPTest/'

for file in os.listdir(batch_dir):
    if file.endswith('.pkl'):
        with open(batch_dir + file, 'rb') as f:
            sim_results = pickle.load(f)

        pop_traces = {}
        psp_amps = {}

        # Extract pop, cell type, and sections
        for pop in sim_results['net']['params']['popParams']:
            if '_stim' in pop:
                continue
            pop_traces[pop] = {}
            pop_traces[pop]['secs'] = {}

            # Get the section specific delays
            for conn in sim_results['net']['params']['connParams'].values():
                if pop == conn['postConds']['pop']:
                    pop_traces[pop]['secs'][conn['sec']] = {}
                    pop_traces[pop]['secs'][conn['sec']]['delay'] = conn['delay']

            # Extract gid for pop (for singe cell batch)
            for cell in sim_results['net']['cells']:
                if cell['tags']['pop'] == pop:
                    pop_traces[pop]['gid'] = cell['gid']
                    break

            # Based on the section delay, extract the slice of the somatic trace
            window_ms = 1500  # ms before and after stimulus
            for sec in pop_traces[pop]['secs'].values():
                window_size = int(window_ms / sim_results['simConfig']['dt'])
                stim_idx = int(sec['delay'] / sim_results['simConfig']['dt'])
                start = stim_idx - window_size
                end = stim_idx + window_size
                trace = sim_results['simData']['V_soma']['cell_' + str(pop_traces[pop]['gid'])]
                sec['trace'] = trace[start:end]

        # Set up plotting for all sec traces and psps
        prePop = sim_results['simConfig']['prePop']
        for pop, pop_data in pop_traces.items():
            pop_dir = os.path.join(batch_dir, f'plots/{pop}_plots/{prePop}->{pop}')
            os.makedirs(pop_dir, exist_ok=True)
            traces = []
            times = None
            psp_amps[pop] = {}
            baseline_window = 50  # Baseline period for psp amplitude

            for sec_name, sec_data in pop_data['secs'].items():
                delay = sec_data['delay']
                trace = sec_data['trace']
                dt = sim_results['simConfig']['dt']
                baseline = np.mean(trace[:baseline_window])
                if prePop in sim_results['simConfig']['Epops'] + sim_results['simConfig']['TEpops']:
                    peak = np.max(trace[baseline_window:])
                else:
                    peak = np.min(trace[baseline_window:])
                amplitude = peak - baseline
                psp_amps[pop][sec_name] = amplitude
                if times is None:
                    times = np.linspace(-window_ms, window_ms, len(trace))
                traces.append(trace)

                # Individual sec traces
                plt.figure()
                plt.plot(times, trace)
                plt.title(f'{prePop} -> {pop}: {sec_name}')
                plt.xlabel('Time (ms)')
                plt.ylabel('V (mV)')
                plt.savefig(os.path.join(pop_dir, f'{sec_name}_trace.png'))
                plt.close()

            # Plot all traces and average
            if traces:
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


        for pop in psp_amps:
            pop_dir = os.path.join(batch_dir, f'plots/{pop}_plots/{prePop}->{pop}')
            os.makedirs(pop_dir, exist_ok=True)

            if len(psp_amps[pop]) > 1:
                # 1. Size summary PSP
                plt.figure()
                plt.boxplot(list(psp_amps[pop].values()))
                plt.title('PSP Amplitudes Across Sections')
                plt.ylabel('Amplitude (mV)')
                plt.savefig(os.path.join(pop_dir, f'psp_amplitudes_summary.png'))
                plt.close()

                # 2. Section vs. soma comparison PSP
                soma_amp = psp_amps[pop].get('soma', None)
                other_amps = [amp for sec, amp in psp_amps[pop].items() if sec != 'soma']
                plt.figure()
                plt.bar(['soma', 'other'], [soma_amp, np.mean(other_amps)])
                plt.title('Soma vs. Other Section PSP Amplitudes')
                plt.ylabel('Amplitude (mV)')
                plt.savefig(os.path.join(pop_dir, f'soma_vs_secs_psp.png'))
                plt.close()
