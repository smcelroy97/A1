import json
import shutil
from pathlib import Path

import numpy as np


def collect_trace_figures(
        dirpath_exp: str | Path
        ) -> None:

    # Create output folder for trace figures
    dirpath_figs_out = dirpath_exp / 'traces'
    dirpath_figs_out.mkdir(exist_ok=True)
    print(f'Output folder: {dirpath_figs_out}')

    # Find all trace figures
    trace_files = list(dirpath_exp.rglob("*_traces.png"))  # incl. subfolders

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
