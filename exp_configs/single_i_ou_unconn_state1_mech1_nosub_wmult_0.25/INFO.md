- Constant OU current input (mean, std), see `ou_inputs.json`, tau=10.
- Isolated populations in a surrogate surrounding (no recurrent connections).
- Surrogate state: `state_1` (see `target_state_1.csv`).
- Subconn is turned off.
- For exc. cells, gKDR is increased to avoid cell-level multistability (see `mech_changes_1.json`)
    It distorts f-I curves compared to experimental data, re-tuning is needed in future.
- 25% connectivity
