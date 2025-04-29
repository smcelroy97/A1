from pathlib import Path

from collect_trace_figures import collect_trace_figures
from create_batch_res_table import create_batch_res_table
from create_batch_voltage_table import create_batch_voltage_table
from gen_regular_grid import gen_regular_grid
from plot_rate_cv_grid import plot_rate_cv_grid
from plot_voltage_metrics_grid import plot_voltage_metrics_grid


# Experiment name
exp_name = '<EXP_NAME>'

# Action flags
need_create_grid = 0
need_calc_result_table = 1
need_calc_voltage_table = 1
need_plot_rate_cv_grid = 1
need_plot_voltage_metrics_grid = 1
need_collect_trace_figures = 1

# Define the ranges and number of points for the grid
ou_mean_range = (-0.06, 0.05)
ou_mean_npoints = 4
ou_std_range = (0, 0.05)
ou_std_npoints = 4

# Time limits for the rate and CV calculation (in seconds)
t_limits = (2, 3)  # in seconds

# Min. number of spikes to use a cell for CV calculation
nspikes_min = 5

# Voltage ranges for metric calculation
v_ranges = [(-200, 0), (-200, -70), (-70, -50), (-50, 0)]

# Voltage metrics to plot on a grid
metrics_vis = [
    'V_median_-200_0',
    (
        'V_(-50_0)_(-70_-50)_num_ratio',
        lambda x: (
            (x['V_num_-50_0'] - x['V_num_-70_-50']) / 
            (x['V_num_-50_0'] + x['V_num_-70_-50'])
        )
    )
]


# Repo root (two levels above this script)
dirpath_base = Path(__file__).resolve().parents[2]

# Experiment config and result folders
dirpath_exp_cfg = dirpath_base / 'exp_configs' / exp_name
dirpath_exp_res = dirpath_base / 'exp_results' / exp_name

# Generate and save the grid
if need_create_grid:
    print('==== CREATE GRID ====')
    fpath_out = dirpath_exp_cfg / 'ou_grid.csv'
    need_save = True
    if fpath_out.exists():
        user_input = input(f"{fpath_out} already exists. Replace it? (y/n): ").strip().lower()
        if user_input != 'y':
            print("Operation cancelled.")
            need_save = False
    if need_save:
        gen_regular_grid(
            ou_mean_range, ou_mean_npoints,
            ou_std_range, ou_std_npoints,
            fpath_out
        )

# Collect rates and CVs from batch result to a csv file
if need_calc_result_table:
    print('==== COMPUTE TABLE OF RESULTS ====')
    create_batch_res_table(dirpath_exp_res, t_limits, nspikes_min)

# Collect voltage metrics from batch result to a csv file
if need_calc_voltage_table:
    print('==== COMPUTE TABLE OF VOLTAGES ====')
    create_batch_voltage_table(dirpath_exp_res, t_limits, v_ranges)

# Plot rate and CV matrices
if need_plot_rate_cv_grid:
    print('==== PLOT RATE AND CV MATRICES ====')
    plot_rate_cv_grid(
        dirpath_exp_res,
        npoints=200,
        show_grid=True,
        show_r_cv_contours=True,
        dirname_out='plots'
    )

# Plot matrices of voltage metrics
if need_plot_rate_cv_grid:
    print('==== PLOT MATRICES OF VOLTAGE MERTRICS ====')
    plot_voltage_metrics_grid(dirpath_exp_res, metrics_vis)

# Copy voltage traces to a separate folder and give them meaningful names
if need_collect_trace_figures:
    print('==== COLLECT TRACES ====')
    collect_trace_figures(dirpath_exp_res)