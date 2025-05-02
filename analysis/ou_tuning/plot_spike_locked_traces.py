from pathlib import Path
import pickle

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from batch_result_manager import BatchResultManager
import netpyne_res_parse_utils as parse_utils
from xr_utils import plot_xr


dirpath_base = Path(
    r'D:\WORK\Salvador\repo\A1_OUinp\exp_results\batch_ougrid_ire_4x4'
)

params = {
    'ou_mean': -0.006,
    'ou_std': 0.02
}

pop_vis = 'IRE'

# Time limits for spike and voltage selection
t_limits = (2, 10)   # in seconds
t_limits_ms = (t_limits[0] * 1000, t_limits[1] * 1000)

# Time window around each spike (epoch)
time_win = (-10, 500)   # in ms


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
    subtract_t0=True,
    ms=True    # get spike times in milliseconds
)
cell_spikes = [s.ravel() for s in cell_spikes]   # make sure spike trains are 1-d
ncells = len(cell_spikes)

# Extract voltages
V_data = parse_utils.get_voltages_xr(sim_res, t_limits_ms)[pop_vis]

# Filter spikes to include only those corresponding to recorded cell gids
pop_cell_gids_all = parse_utils.get_pop_cell_gids(sim_res, pop_vis)
pop_cell_gids_rec = V_data.coords['cell_gid'].values
cell_spikes_rec = [
    cell_spikes[pop_cell_gids_all.index(gid)]
    for gid in pop_cell_gids_rec
]

tvec = V_data.coords['time'].values
dt = tvec[1] - tvec[0]
time_win_bins = (int(time_win[0] / dt),
                 int(time_win[1] / dt))

# Compute spike-triggered voltage traces
Vtrig = []
for cell_num, spikes in enumerate(cell_spikes_rec):
    for spike_time in spikes:
        # Extract the time window around the spike
        start_bin = int(spike_time / dt) + time_win_bins[0]
        end_bin = int(spike_time / dt) + time_win_bins[1] + 1
        if (start_bin >= 0) and (end_bin <= V_data.shape[1]):
            trace = V_data[cell_num, start_bin : end_bin].values.ravel()
            Vtrig.append(trace)

# Collect spike_triggered_traces to xarray
Vtrig = np.vstack(Vtrig)
tvec_epoch = np.linspace(time_win[0], time_win[1], Vtrig.shape[1])
Vtrig = xr.DataArray(
    Vtrig,
    dims=("spike", "time"),
    coords={"spike": np.arange(Vtrig.shape[0]),
            "time": tvec_epoch},
)

matplotlib.use('Qt5Agg', force=True)

#plt.ion()
plt.figure()

plt.subplot(2, 1, 1)
plot_xr(Vtrig)
plt.ylabel('Spikes')
plt.title(f'Spike-locked voltage traces for {pop_vis}')

plt.subplot(2, 1, 2)
Vtrig_avg = Vtrig.mean(dim='spike')
plt.plot(tvec_epoch, Vtrig_avg)
plt.xlabel('Time, ms')
plt.ylabel('Mean voltage')

plt.show()
