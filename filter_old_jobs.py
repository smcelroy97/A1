import os
import json
import shutil
import re
import pandas as pd
from pathlib import Path


def filter_old_jobs(dirpath_res: Path, df: pd.DataFrame):
    dirpath_res = Path(dirpath_res)
    df = df.copy()

    # Check for any *_data.pkl files (evidence of a previous run)
    data_files = list(dirpath_res.rglob("*_data.pkl"))  # incl. subfolders
    if not data_files:
        print("No *_data.pkl files found.")
        return df

    # Generate name for the subfoldder folder to move previous runs: old_run_{n}
    existing_old_runs = [d for d in dirpath_res.iterdir()
                         if d.is_dir() and re.match(r"old_run_\d+", d.name)]
    if existing_old_runs:
        max_n = max(int(re.search(r"\d+", d.name).group()) for d in existing_old_runs)
        new_run_folder = dirpath_res / f"old_run_{max_n + 1}"
    else:
        new_run_folder = dirpath_res / "old_run_1"

    # Process each *_cfg.json file
    cfg_files = list(dirpath_res.rglob("*_cfg.json"))  # incl. subfolders
    for cfg_file in cfg_files:
        with open(cfg_file) as f:
            cfg = json.load(f)

        # Read OUamp and OUstd from json
        OUamp = cfg.get('simConfig', {}).get('OUamp')
        OUstd = cfg.get('simConfig', {}).get('OUstd')
        if OUamp is None or OUstd is None:
            print(f"Skip {cfg_file.name}: missing OUamp or OUstd")
            continue
        
        # Check whether the job corresponding to the current cfg file
        # had produced a reulting pkl file
        base_name = cfg_file.stem[:-4]  # strip _cfg
        pkl_file = cfg_file.parent / f"{base_name}_data.pkl"
        if not pkl_file.exists():
            print(f"Skip {cfg_file.name}: no corresponding *_data.pkl file")
            #print(f'Path: {pkl_file}')
            continue

        # Find and remove df rows that match the cfg file
        tol = 1e-8  # rounding tolerance
        match = df[((df['ou_mean'] - OUamp).abs() < tol) &
                    ((df['ou_std'] - OUstd).abs() < tol)]
        if match.empty:
            print(f"{cfg_file.name}: no matching row ({OUamp}, {OUstd}) in df"
                  " - possibly a duplicate, removed from df before")
            print(f'Path: {cfg_file}')
        else:
            df.drop(match.index, inplace=True)
            print(f"Remove the row with (OUamp={OUamp}, OUstd={OUstd}) from df")

        # If the job result is already in a subfolder - do nothing
        if cfg_file.parent != dirpath_res:
            continue

        # Get all to-be-moved files from the dirpath_res root
        fnames_move = list(dirpath_res.glob(f"*{base_name}*"))

        # If there are files to move - create a subfolder old_run_{n}
        if fnames_move and not new_run_folder.exists():
            new_run_folder.mkdir()
            print(f"Create a subfolder to move the previous results: {new_run_folder}")

        # Move all files related to the current job to old_run_{n} subfolder
        for f in fnames_move:
            shutil.move(str(f), new_run_folder / f.name)
            print(f"Moved file: {f.name}")

    return df


if __name__ == '__main__':
    
    dirpath_self = Path(__file__).resolve().parent
    exp_name = 'batch_ougrid_pv_0'
    dirpath_res = dirpath_self / 'exp_results' / exp_name

    # Read a list of (ou_mean, ou_std) tuples from a CSV file
    fpath_ou_grid = dirpath_self / 'exp_configs' / exp_name / 'ou_grid.csv'
    df = pd.read_csv(fpath_ou_grid)

    # Run the filtering function
    df_filt = filter_old_jobs(dirpath_res, df)
    print(df_filt)