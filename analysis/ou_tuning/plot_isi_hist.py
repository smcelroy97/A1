from pathlib import Path
import pickle

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from batch_result_manager import BatchResultManager
import netpyne_res_parse_utils as parse_utils


dirpath_base = Path(
    r'D:\WORK\Salvador\repo\A1_OUinp\exp_results\batch_i_ougrid_its4_20x20_tau_10'
)

params = {
    'ou_mean': 0.001,
    'ou_std': 0.001
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

matplotlib.use('Qt5Agg', force=True)

# Plot ISI histograms
#plt.ion()
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(bins[:-1], h)
plt.title(f'Histogram of {pop_vis} ISI')
plt.xlabel('ISI, ms')

plt.subplot(1, 2, 2)
extent = (bins[0], bins[-1], 0, ncells)
plt.imshow(H, aspect='auto', interpolation='nearest',
           extent=extent)
#plt.colorbar(label='Density')
plt.xlabel('ISI, ms')
plt.ylabel('Cells')

#plt.draw()
plt.show()