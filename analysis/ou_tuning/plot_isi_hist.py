import os
from pathlib import Path
import pickle

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gamma

from batch_result_manager import BatchResultManager
import netpyne_res_parse_utils as parse_utils


dirpath_base = Path(
    '/ddn/smcelroy97/A1-OUinp/exp_results/batch_i_ougrid_its4_20x20_tau_2_10sec_small'
)

params = {
    'ou_mean': 0.0003,
    'ou_std': 0.0065
}

pop_vis = 'ITS4'

t_limits=(2, 10)   # in seconds

nbins = 50


# Get path to the data by job params
batch_res_mgr = BatchResultManager(dirpath_base)
fpath_sim_res = batch_res_mgr.job_data_fpath_by_params(params)
print(fpath_sim_res)

# Load sim result
with open(fpath_sim_res, 'rb') as fid:
    sim_res = pickle.load(fid)

# Extract spikes
cell_spikes = parse_utils.get_pop_spikes(
    sim_res, pop_vis, combine_cells=False,
    t0=t_limits[0], tmax=t_limits[1],
    ms=True    # get spike times in milliseconds
)
cell_spikes = [s.ravel() for s in cell_spikes]   # make sure spike trains are 1-d
ncells = len(cell_spikes)

# Calculat ISI
cell_ISI = [s[1:] - s[:-1] for s in cell_spikes]
all_ISI = np.hstack(cell_ISI)

# Histogram (cells combined)
h, bins = np.histogram(all_ISI, bins=nbins,
                       density=True)

# Histograms (per cell)
H = np.zeros((ncells, nbins))
for n in range(ncells):
    H[n, :], _ = np.histogram(cell_ISI[n], bins=bins,
                              density=True)

# Fit gamma distribution to the histogram
gamma_k, gamma_loc, gamma_scale = gamma.fit(all_ISI, floc=0)
h_gamma = gamma.pdf(bins[:-1], gamma_k, loc=gamma_loc, scale=gamma_scale)

#matplotlib.use('Agg', force=True)

# Plot ISI histograms
#plt.ion()
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(bins[:-1], h)
plt.plot(bins[:-1], h_gamma, 'k--')
plt.title(f'Histogram of {pop_vis} ISI (cells combined)')
plt.xlabel('ISI, ms')
plt.ylim(0, 0.008)
plt.xlim(-10, 1000)
plt.ylim(0, 0.01)

# Add a text box to the top-right corner of the plot
r = 1000. / gamma_k / gamma_scale
CV = np.sqrt(1 / gamma_k)
text_str = (
    f'Gamma_k: {gamma_k:.2f}\n'
    f'Rate: {r:.2f} Hz\n'
    f'CV: {CV:.2f}'
)
plt.text(0.95, 0.95, text_str,
         horizontalalignment='right',
         verticalalignment='top',
         transform=plt.gca().transAxes,
         bbox=dict(facecolor='white', edgecolor='black'))

plt.subplot(1, 2, 2)
extent = (bins[0], bins[-1], 0, ncells)
plt.imshow(H, aspect='auto', interpolation='nearest',
           extent=extent)
#plt.colorbar(label='Density')
plt.title(f'Histogram of {pop_vis} ISI (per cell)')
plt.xlabel('ISI, ms')
plt.ylabel('Cells')

#plt.draw()
plt.show()

dirpath_out = dirpath_base / 'plots_ISI'
os.makedirs(dirpath_out, exist_ok=True)
fname_fig = (f'ISI_hist_{pop_vis}'
             f'_oumean_{params["ou_mean"] * 100 : .02f}'
             f'_oustd_{params["ou_std"] * 100 : .02f}'
             '.png')
fpath_out = dirpath_out / fname_fig
plt.savefig(fpath_out, dpi=300)

