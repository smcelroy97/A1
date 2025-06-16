import pickle
import os
import matplotlib; matplotlib.use('macosx')
from matplotlib import pyplot as plt

batch_dir = '../simOutput/PSPTest/'

for file in os.listdir(batch_dir):
    if file.endswith('.pkl'):
        with open(batch_dir + file, 'rb') as f:
            sim_results = pickle.load(f)

        pop_traces = {}
        for pop in sim_results['net']['params']['popParams']:
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

            plt.figure()
            for sec, item in pop_traces[pop]['secs'].items():
                plt.plot(item['trace'])
                plt.savefig('testPSP_' + str(pop) + '.png')
