from pathlib import Path
import pickle

import matplotlib
import matplotlib.pyplot as plt

from batch_result_manager import BatchResultManager
import netpyne_res_parse_utils as parse_utils

exp_name = 'batch_i_ougrid_its4_20x20_tau_2_10sec_small'

dirpath_base = Path(
    r'/ddn/smcelroy97/A1-OUinp/exp_results/' + exp_name 
)

voltage_plots_dir = dirpath_base / 'plots_voltage'

params = {
    'ou_mean': -0.0008,
    'ou_std': 0.0067
}

pop_vis = 'ITS4'

# Get path to the data by job params
batch_res_mgr = BatchResultManager(dirpath_base)
fpath_sim_res = batch_res_mgr.job_data_fpath_by_params(params)
print(fpath_sim_res)

job_id = Path(fpath_sim_res).stem.split('_')[-2]
print(f"Extracted job ID: {job_id}")

# Extract the exact params used for plot
exact_params = batch_res_mgr.job_params_by_id(int(job_id))
print(f'Exact params: {exact_params}')

# Multiply exact params by 100 and round to two significant figures
ou_mean_exact = round(exact_params['ou_mean'] * 100, 2)
ou_std_exact = round(exact_params['ou_std'] * 100, 2)

# Save the plot with exact ou_mean and ou_std in the filename
output_filename = f'hist_{pop_vis}_oumean_{ou_mean_exact}_oustd_{ou_std_exact}.png'
output_path = voltage_plots_dir / output_filename

# Load sim result
with open(fpath_sim_res, 'rb') as fid:
    sim_res = pickle.load(fid)

# Extract voltages
V_data, _ = parse_utils.get_voltages(sim_res, t_limits=(2000, 3000))

matplotlib.use('Agg', force=True)

# Plot voltage histogram
#plt.ion()
plt.figure()
plt.hist(V_data[pop_vis].ravel(), bins=50, color='blue', alpha=0.7)
plt.title(f'Histogram of {pop_vis} voltages')
plt.xlabel('Voltage (mV)')
plt.draw()
plt.savefig(output_path)
print(f"Plot saved to {output_path}")
plt.close()