Tuning a revised A1 model:
- Params from "samn" branch of the A1 NKI repo (commit: ca5f892),
    excluding wmat from trial_2142_cfg.json
- All gains set to 1
- Subconn is used
- IT/PT/CT params are modified to avoid cell-level multistability
- Old background inputs removed
- New background inputs (OU) is tuned to achieve a required regime