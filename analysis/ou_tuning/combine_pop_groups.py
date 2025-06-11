import os
from pathlib import Path
import shutil


# Sim results root folder
dirpath_base = Path(__file__).resolve().parents[2] / 'exp_results'

# Experiment names
exp_names = [
    'batch_i_ougrid_ct_20x20_tau_2_10sec',
    'batch_i_ougrid_it23_20x20_tau_2_10sec_1',
    'batch_i_ougrid_it5b6_20x20_tau_2_10sec',
    'batch_i_ougrid_itp4_20x20_tau_2_10sec_1',
    'batch_i_ougrid_its4_20x20_tau_2',
    'batch_i_ougrid_ngf_20x20_tau_2_10sec',
    'batch_i_ougrid_pv_20x20_tau_2_10sec',
    'batch_i_ougrid_som_20x20_tau_2_10sec',
    'batch_i_ougrid_tc_20x20_tau_2_10sec',
    'batch_i_ougrid_thal_inhib_20x20_tau_2_10sec',
    'batch_i_ougrid_ti_20x20_tau_2_10sec',
    'batch_i_ougrid_vip_20x20_tau_2_10sec_1',
    'batch_i_ougrid_it5a_20x20_tau_2_10sec'
]
exp_names = [f'batch_i_ougrid/{name}' for name in exp_names]

# Name of the folder to combine
#dirname_sub = 'plots_r_cv_slices_mu0_0.000'
dirname_sub = 'plots_r_cv_slices_mu0_-0.010'

# Target folder for combined data
dirname_out = 'batch_i_ougrid/batch_i_ougrid_all'

# Create output folder
dirpath_out = dirpath_base / dirname_out / dirname_sub
os.makedirs(dirpath_out, exist_ok=True)

for exp_name in exp_names:
    dirpath_in = dirpath_base / exp_name / dirname_sub
    for fpath_in in dirpath_in.iterdir():
        shutil.copy(fpath_in, dirpath_out)

