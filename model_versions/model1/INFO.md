- Tuned for the firing rates: `target_state_1.csv`

- Original A1 model with all gains set to 1
- Original weights are reduced to 25%

- Subconn is turned off.
- For exc. cells, gKDR is increased to avoid cell-level multistability (see `mech_changes_1.json`)
    It distorts f-I curves compared to experimental data, re-tuning is needed in future.

- Background: OU current, `tau=10`
- (ou_mean, ou_std) is tuned for each population 
- Initial tuning is done with a grid search, see:
    `exp_results/batch_i_ougrid_unconn_state1_mech1_nosub_wmult_0.25/all/exp_ou_nmean_16_nstd_16/combined`
- Additional tuning is done using rate-controlling feedback, see:
    `exp_results/single_i_ou_subnet_state1_mech1_nosub_wmult_0.25/full_model_split_ee_conn/exp_t_46.0_50.0_eefrac_0.5_kmu_0.1_ksigma_0.0_tau_200_taus_2500_tc0_2000_tlock_40000_kci_0.0005_kcp_0.0/traces`

- Split E-E connections into surrogate (static) and active parts
- Fraction of the active part for E-E is 0.5
- Surrogate state: `target_state_1.csv`
