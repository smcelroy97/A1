Created for single-cell tuning. Goals:
- Destroy multi-stability
- Spare the original f-I curves

Main file to run: `init.py`

Description of the setting (params are defined in `cfg.py`):
- One population of unconnected cells: `POP_ACTIVE`. As an example, `IT5A` is used.
- Each cell receives a constant input ("I" of the f-I curve).
- These inputs change gradually across cells, so the read-out of the firing rates from the whole population yields f-I curve. The range is given by `cfg.OUamp`.
- Every cell receives a transient ramp-up current-based stimulus in the middle of simulation, whose purpose is to switch the cell to a different steady state. Its amplitude is given by `cfg.ou_ramp_offset`.
- Additionally, every cell receives a NetStim input. It is intended to be weak and serves to create random jumping between steady-states. Its params are `cfg.bkg_r` (rate) and `cfg.bkg_w` (weight).
- One of the membrane mechanisms can be modified (for every section of every cell), see `cfg.mech_changes`. The parameter I changed to destroy multistability is `gbar` of `kdr` mechanism. Set `mult=1` for the original multistable behavior or `mult=3` for monostability.

The f-I curve is mainly defined by `cfg.OUamp` and `cfg.mech_changes`. Stimulus (`cfg.ou_ramp_offset`) and noise (`cfg.bkg_r`, `cfg.bkg_w`) are for highlighting various f-I curve branches.

Output:
- Simulation results are saved into `sim_output` folder.
- Calculation of f-I curves is done in `post_run.py`.
- The curves are saved to `fi_curve_IT5A.png` files.
- Blue dots show pre-stimulus firing rates, orange dots - post-stimulus firing rates. Orange dots are slighly shifted vertically for better visualization.
- For better understaning of the setup, see the raster plots.

Example: `sim_output/sim_IT5A_kdr_mult_1_ramp_1.5_rx_75_wx_0.5/fi_curve_IT5A.png`
- Before the stimulus, two spiking regimes exist (with different rates) for a certain range of inputs.
- The stimulus kicks the cells into depolarization block, which is stable in a large range of inputs.
- So for any input value that can produce spiking, depolarization block is a stable solution. Cells eacsily stuck in the block due to random fluctuations, and the spiking terminates.

In `sim_output/sim_IT5A_kdr_mult_3_ramp_1.5_rx_75_wx_0.5/fi_curve_IT5A.png`, there exists an input range where spiking occurs (with a single spiking regime), while depolarization block doesn't exist as a stable solution.
