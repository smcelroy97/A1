- Probe OU current inputs from a (mean, std) grid, `tau=10`
- Probed `ou_mean` and `ou_std` ranges are given for each pop. separately, see `ou_ranges.csv`
- Isolated populations in a surrogate surrounding (no self-connection).
- Surrogate state: `state_1` (see `target_state_1.csv`).
- Subconn is turned off.
- For exc. cells, gKDR is increased to avoid cell-level multistability (see `mech_changes_1.json`)
    It distorts f-I curves compared to experimental data, re-tuning is needed in future.
