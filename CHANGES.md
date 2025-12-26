# Changes

This document outlines the changes made to the simulation configuration and network parameter files.

## 1. Configuration and Network Parameter Consolidation

- **Consolidated `cfg.py` and `cfg_base.py` into `cfg_new.py`**:
  - The base configuration from `cfg_base.py` and the modifications from `cfg.py` were merged into a single file, `cfg_new.py`.
  - This new file contains the complete configuration for the simulation.

- **Consolidated `netParams.py` and `netParams_base.py` into `netParams_new.py`**:
  - The base network parameters from `netParams_base.py` and the modifications from `netParams.py` were merged into a single file, `netParams_new.py`.
  - This new file contains the complete network parameter definition for the simulation.

## 2. Simplification and Refactoring

- **Hardcoded Simulation-Specific Parameters**:
  - The configuration and network parameter files were simplified by hardcoding the values that are specific to the simulation run initiated by `init.py`.
  - This was based on the assumption that the final state of the `cfg` object is the only relevant one.

- **Removed Unused Code and Parameters**:
  - Conditional blocks in `netParams_new.py` that were not relevant to the specific simulation case (e.g., `cfg.pops_active` being `['IT5A']`) were removed.
  - Unused synaptic mechanism definitions were removed from `netParams_new.py`. The only remaining mechanism is 'AMPA'.
  - Unused connectivity and gain-related configurations were removed from `cfg_new.py`.

## 3. Entry Point Update

- **Updated `init.py`**:
  - The main simulation script, `init.py`, was updated to import the consolidated and simplified configuration and network parameters from `cfg_new.py` and `netParams_new.py`.
  - The line `from netParams import cfg, netParams` was replaced with `from netParams_new import cfg, netParams`.
