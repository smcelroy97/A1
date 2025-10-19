- These are configs for experiments controlled by SimManagerHPCBatch
- SimManagerHPCBatch starts opt_batch_script.py, which submits jobs
- Variable params are provided by SimManagerHPCBatch via `requests.json` files
- Example: ...
- Conversion from requests to cfg fields is done in `batch_params.py -> post_update()`

- Connectivity strength: 25%
- OU current inputs with `tau=10`
- Surrogate state: `state_1` (see `target_state_1.csv`).
- Subconn is turned off.
- For exc. cells, gKDR is increased to avoid cell-level multistability (see `mech_changes_1.json`)
    It distorts f-I curves compared to experimental data, re-tuning is needed in future.