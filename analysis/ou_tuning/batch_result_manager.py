import json
import shutil
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import xarray as xr


class BatchResultManager:

    def __init__(self, dirpath_exp: Path | str):
        self.dirpath_exp = Path(dirpath_exp)

        self._job_name_base = ''
        self._params_by_job_id: Dict[str, Dict[str, float]] = {}
        self._job_idx_by_params: pd.DataFrame | None = None

        self.param_names = ['ou_mean', 'ou_std']
        self.cfg_param_fields = {
            'ou_mean': 'OUamp',
            'ou_std': 'OUstd'
        }

        self._collect_batch_params()

    def _collect_batch_params(self):
        self._params_by_job_id = {}
        job_idx_by_params = []

        # Find all cfg files
        cfg_files = list(self.dirpath_exp.rglob("*_cfg.json"))  # incl. subfolders

        self._job_name_base = cfg_files[0].stem[:-10]   # file name without "_cfg" and job id

        # Read params from cfg files
        for fpath_cfg in cfg_files:
            # Read cfg file
            with open(fpath_cfg) as f:
                cfg = json.load(f)
            
            # Read batch param values from cfg
            params = {}
            for par_name in self.param_names:
                field_name = self.cfg_param_fields[par_name]
                params[par_name] = cfg['simConfig'][field_name]

            # Job ID -> params
            job_id = int(fpath_cfg.stem.split('_')[-2])
            self._params_by_job_id[job_id] = params

            # Params -> job ID
            par_lst = [params[par_name] for par_name in self.param_names]
            job_idx_by_params.append(par_lst + [job_id])
        
        self._job_idx_by_params = pd.DataFrame(
            data=job_idx_by_params,
            columns=([self.param_names + ['job_id']])
        )
    
    def job_params_by_id(self, job_id: int) -> Dict[str, float]:
        return self._params_by_job_id[job_id]

    def job_id_by_params(self, job_par: Dict[str, float]) -> int:
        # Find the closest matching parameters
        npar = len(self.param_names)
        par_vals_arg = np.array(
            [job_par[par_name] for par_name in self.param_names]).reshape(1, npar)
        par_vals_tbl = self._job_idx_by_params[self.param_names].values.reshape(-1, npar)
        dvec = np.sum((par_vals_tbl - par_vals_arg)**2, axis=1)
        closest_row = np.argmin(dvec)
        return int(self._job_idx_by_params.loc[closest_row, 'job_id'].iloc[0])
    
    def job_name_by_id(self, job_id: int) -> str:
        return f'{self._job_name_base}_{job_id:05d}'
    
    def job_data_fpath_by_id(self, job_id: int) -> str:
        job_name = self.job_name_by_id(job_id)
        return str(self.dirpath_exp / f'{job_name}_data.pkl')
    
    def job_name_by_params(self, job_par: Dict[str, float]) -> str:
        job_id = self.job_id_by_params(job_par)
        return self.job_name_by_id(job_id)
    
    def job_data_fpath_by_params(self, job_par: Dict[str, float]) -> str:
        job_id = self.job_id_by_params(job_par)
        return self.job_data_fpath_by_id(job_id)
