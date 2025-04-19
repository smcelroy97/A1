import os
import json
import shutil
import re
import pandas as pd
from pathlib import Path

import numpy as np


#exp_name = 'batch_ougrid_itp4_10x10_large_oubal'
exp_name = 'batch_ougrid_itp4_4x4_med_3s'

dirpath_base = Path(__file__).resolve().parents[2]
dirpath_res = dirpath_base / 'exp_results' / exp_name
print(f'Input folder: {dirpath_res}')

# Create output folder for trace figures
dirpath_figs_out = dirpath_base / 'exp_results' / exp_name / 'traces'
dirpath_figs_out.mkdir(exist_ok=True)
print(f'Output folder: {dirpath_figs_out}')

# Find all trace figures
trace_files = list(dirpath_res.rglob("*_traces.png"))  # incl. subfolders

# Collect file info first
file_info = []
for fpath_trace in trace_files:

    fpath_cfg = fpath_trace.parent / f'{fpath_trace.stem[:-7]}_cfg.json'
    with open(fpath_cfg) as f:
        cfg = json.load(f)

    ou_mean = np.round(cfg.get('simConfig', {}).get('OUamp') * 100, 2)
    ou_std = np.round(cfg.get('simConfig', {}).get('OUstd') * 100, 2)

    file_info.append((ou_mean, ou_std, fpath_trace))

# Sort by ou_mean, then ou_std
file_info.sort()

# Copy files with order number added
for n, (ou_mean, ou_std, fpath_trace) in enumerate(file_info, start=1):
    print(f'Copy: {fpath_trace.name}')
    fname_out = f'{n:03d}_oumean_{ou_mean}_oustd_{ou_std}.png'
    fpath_out = dirpath_figs_out / fname_out
    shutil.copy(fpath_trace, fpath_out)

""" 
for n, fpath_trace in enumerate(trace_files):
    print(f'Copy: {fpath_trace.name}')

    # Read *_cfg.json file corresponding to the current figure
    fpath_cfg = fpath_trace.parent / f'{fpath_trace.stem[:-7]}_cfg.json'
    with open(fpath_cfg) as f:
        cfg = json.load(f)

    # Read OUamp and OUstd from config json
    ou_mean = cfg.get('simConfig', {}).get('OUamp')
    ou_std = cfg.get('simConfig', {}).get('OUstd')

    # Path to the renamed copy of the current figure
    ou_mean = np.round(ou_mean * 100, 2)
    ou_std = np.round(ou_std * 100, 2)
    #fname_out = f'{exp_name}_oumean_{ou_mean}_oustd_{ou_std}_traces.png'
    fname_out = f'oumean_{ou_mean}_oustd_{ou_std}.png'
    fpath_out = dirpath_figs_out / fname_out

    # Copy and rename the figure
    shutil.copy(fpath_trace, fpath_out) """
