- These are configs for experiments controlled by SimManagerHPCBatch
- SimManagerHPCBatch starts opt_batch_script.by, which submits jobs
- Variable params are provided by SimManagerHPCBatch via `requests.json` files
- Example: `exp_results/sim_manager_batch/exp_subnet_state1_mech1_nosub_wmult_0.1/exp_test_1/requests/requests.json`
- Conversion from requests to cfg fields is done in `batch_params.py -> post_update()`

- OU current inputs with `tau=10`
- Surrogate state: `state_1` (see `target_state_1.csv`).
- Subconn is turned off.
- For exc. cells, gKDR is increased to avoid cell-level multistability (see `mech_changes_1.json`)
    It distorts f-I curves compared to experimental data, re-tuning is needed in future.