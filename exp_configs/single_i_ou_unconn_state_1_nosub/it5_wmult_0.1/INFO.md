- Single simulation of IT5A and IT5B cells to check the selected OU inputs (see `ou_inputs.json`).
- OU selection is based on: `exp_results/batch_i_ougrid_unconn_state1_nosub_wmult_0.1/pyr/exp_ou_nmean_10_nstd_10`
- Notebook for OU selection: `exp_configs/batch_i_ougrid_unconn_state1_nosub_wmult_0.1/explore_result.ipynb`

It seems that these cells need a long time to stabilize, so the actual firing rate is higher than the target (7 vs 5 Hz). This exp is intended to check a longer run.
