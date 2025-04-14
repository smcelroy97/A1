import os
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd


# Define the ranges and number of points for the grid
ou_mean_range = (-2, 2)
ou_std_range = (-1, 1)
npoints = 500

# Surrogate pop names
pop_names = ['POP1', 'POP2', 'POP3']

# Name of the surrogate "experiment"
exp_name = 'grid_test_surrogate'

# Output folder
dirpath_base = (
    Path(__file__).resolve().parents[2] /  # two levels above this script
    'exp_results' / exp_name
)
os.makedirs(dirpath_base, exist_ok=True)
print(f'Output folder: {dirpath_base}')

# Generate randomly distributed points
ou_mean_values = np.random.uniform(ou_mean_range[0], ou_mean_range[1], npoints)
ou_std_values = np.random.uniform(ou_std_range[0], ou_std_range[1], npoints)

def rate_gen_func(ou_mean, ou_std, pop_num):
    """Generate surrogate rate values. """
    return ou_mean**2 + ou_std**2 + pop_num

def cv_gen_func(ou_mean, ou_std, pop_num):
    """Generate surrogate CV values. """
    return (ou_mean - ou_std)**2 + pop_num

data = {'ou_mean': ou_mean_values, 'ou_std': ou_std_values}

# Generate surrogate rate and CV values for each pop
for n, pop in enumerate(pop_names):
    rate_values = rate_gen_func(ou_mean_values, ou_std_values, n)
    cv_values = cv_gen_func(ou_mean_values, ou_std_values, n)
    data[f'{pop}_r'] = rate_values
    data[f'{pop}_cv'] = cv_values

# Save the result as a CSV file
df = pd.DataFrame(data)
fpath_out = dirpath_base / 'batch_result.csv'
df.to_csv(fpath_out, index=False)
