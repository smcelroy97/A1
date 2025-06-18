import pickle
import os
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

batch_dir = '../simOutput/v45_batch23/'

for file in os.listdir(batch_dir):
    if file.endswith('.pkl'):
        with open(batch_dir + file, 'rb') as f:
            sim_results = pickle.load(f)

        pop_traces = {}
        for pop in sim_results['net']['params']['popParams']:
            if '_stim' in pop:
                continue
            pop_traces[pop] = {}
            pop_traces[pop]['secs'] = {}
            for conn in sim_results['net']['params']['connParams'].values():
                if pop == conn['postConds']['pop']:
                    pop_traces[pop]['secs'][conn['sec']] = {}
                    pop_traces[pop]['secs'][conn['sec']]['delay'] = conn['delay']

            for cell in sim_results['net']['cells']:
                if cell['tags']['pop'] == pop:
                    pop_traces[pop]['gid'] = cell['gid']
                    break

            for sec in pop_traces[pop]['secs'].values():
                window_size = int(1500 / sim_results['simConfig']['dt'])
                stim_idx = int(sec['delay'] / sim_results['simConfig']['dt'])
                start = stim_idx - window_size
                end = stim_idx + window_size
                trace = sim_results['simData']['V_soma']['cell_' + str(pop_traces[pop]['gid'])]
                sec['trace'] = trace[start:end]

        window_ms = 1500  # ms before and after stimulus
        prePop = sim_results['simConfig']['prePop']
        for pop, pop_data in pop_traces.items():
            pop_dir = os.path.join(batch_dir, f'plots/{pop}_plots/{prePop}->{pop}')
            os.makedirs(pop_dir, exist_ok=True)

            traces = []
            times = None

            for sec_name, sec_data in pop_data['secs'].items():
                delay = sec_data['delay']
                trace = sec_data['trace']
                dt = sim_results['simConfig']['dt']
                window_size = int(window_ms / dt)
                # The trace is already windowed in your code, so use it directly
                trace_window = trace
                if times is None:
                    times = np.linspace(-window_ms, window_ms, len(trace_window))
                traces.append(trace_window)

                prePop = sim_results['simConfig']['prePop']
                plt.figure()
                plt.plot(times, trace_window)
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