from pathlib import Path
import sys
import os
from netpyne import sim

import matplotlib.pyplot as plt

# Add the repo folder for imports
dirpath_repo_root = Path().resolve()
sys.path.append(str(dirpath_repo_root))
print(f'Repo root: {dirpath_repo_root}')

from analysis.ou_tuning import batch_utils
from plot_fi_vi_curves import plot_fi_curve, plot_vi_curve
from post_run import post_run

dirpath_exp = (dirpath_repo_root / 'batch' / 'gridnax0_0p5_kap0_3')

sim.initialize()
for file in os.listdir(dirpath_exp):
    if file.endswith('_data.pkl'):
        all = sim.loadSimData(f"{dirpath_exp}/{file}")
        post_run(sim)

