This is a full-model test for the OU inputs chosen based on a subnet batch experiment.

Weight multiplier: 0.02

Subnet experiment: `batch_g_ou_subnet_wmult_0.02_all` \
The surrogate model contained all pops. (disconnected) and their Poisson duplicates ("frozen pops.") as the inputs. \
Rates of the Poisson generators were taken from `frozen_rates.csv` \
For each pop., a range of `ou_mean` values was set (`ou_mean_ranges.csv`), and the batch uniformly sampled `ou_mean` values from this range. \
Batch over `ou_mean` values was done for all pops. in parallel (ok, as they are disconnected). \
The values of `ou_std` were calculated with the formula: \
`ou_std = 0.4 * ou_mean + 0.005`




