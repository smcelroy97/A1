import os
from scipy.signal import welch
from batch_result_manager import BatchResultManager
import netpyne_res_parse_utils as parse_utils
from pathlib import Path
import pickle
import numpy as np
from matplotlib import pyplot as plt
import matplotlib
matplotlib.use('Agg', force=True)

dirpath_base = Path(
    '/ddn/smcelroy97/A1-OUinp/exp_results/batch_i_ougrid_its4_20x20_tau_2_10sec_small'
)

plot_individual_cells = True
plot_pop_avg = True

params = {
    'ou_mean': 0.002,
    'ou_std': 0.0125
}

pop_vis = 'ITS4'

t_limits = (2, 10)  # in seconda

fs = 1000

# Get path to the data by job params
batch_res_mgr = BatchResultManager(dirpath_base)
fpath_sim_res = batch_res_mgr.job_data_fpath_by_params(params)
print(fpath_sim_res)

# Load sim result
with open(fpath_sim_res, 'rb') as fid:
    sim_res = pickle.load(fid)

# Extrace voltages
v_data, tvec = parse_utils.get_voltages(sim_res, t_limits=(2000, 3000))

Pxx_all = []
for v_cell in v_data['ITS4']:  # Iterate over each cell's voltage trace
    f, Pxx = welch(v_cell, fs, nperseg=1024)
    Pxx_all.append(Pxx)

# Average the PSDs across the population
Pxx_mean = np.mean(Pxx_all, axis=0)

dirpath_out = dirpath_base / 'plots_PSD'
os.makedirs(dirpath_out, exist_ok=True)

if plot_individual_cells:
    for idx, cell in enumerate(Pxx_all):
        plt.figure()
        plt.semilogy(f, Pxx_all[idx])
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Power Spectral Density')
        plt.title('Averaged PSD Across Population')
        plt.xlim(0, 50)
        plt.show()
        fname_fig = (f'Vm_PSD_{pop_vis}_{idx}'
                     f'_oumean_{params["ou_mean"] * 100}'
                     f'_oustd_{params["ou_std"] * 100}'
                     '.png')
        fpath_out = dirpath_out / fname_fig
        plt.savefig(fpath_out, dpi=300)

if plot_pop_avg:
    # Plot the averaged PSD
    plt.figure()
    plt.semilogy(f, Pxx_mean)
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Power Spectral Density')
    plt.title('Averaged PSD Across Population')
    plt.xlim(0, 50)
    plt.show()
    fname_fig = (f'Vm_PSD_{pop_vis}'
                 f'_oumean_{params["ou_mean"] * 100}'
                 f'_oustd_{params["ou_std"] * 100}'
                 '.png')
    fpath_out = dirpath_out / fname_fig
    plt.savefig(fpath_out, dpi=300)
