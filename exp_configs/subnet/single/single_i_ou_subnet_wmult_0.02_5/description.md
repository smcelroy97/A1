This is a full-model test for the OU inputs chosen based on a subnet batch experiment.

Weight multiplier: 0.02

Subnet experiment: `batch_i_ou_subnet_wmult_0.02_all_5_5s_15pts` \
The surrogate model contained all pops. (disconnected) and their Poisson duplicates ("frozen pops.") as the inputs. \
Rates of the Poisson generators were taken from `frozen_rates.csv` \
For each pop., a range of `ou_mean` values was set (`ou_mean_ranges.csv`), and the batch uniformly sampled `ou_mean` values from this range. \
Batch over `ou_mean` values was done for all pops. in parallel (ok, as they are disconnected). \
The values of `ou_std` were calculated with the formula: \
`ou_std = 0.2 * ou_mean + 0.002`  (1)

The results of the surrogate model batch (rate vs. ou_mean) were fitted by the script:
`model_tuner/proto/subnet_opt/subnet_opt.py`
Working folder:
`model_tuner/test_data/main/test_subnet_opt_A1/i_ou_wmult_0.02_5`

With the fitted functions, target rates (same as frozen_rates) were projected to `ou_mean`, and `ou_std` values were calculated using (1). The results were put into `ou_inputs.json` file, which was used as the input for this full-model simulation.