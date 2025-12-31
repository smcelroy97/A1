# Refactoring for Single-Cell Tuning

This document summarizes the refactoring from a complex, full-network configuration to a simplified, self-contained setup for the specific purpose of **single-cell tuning**.

The original system, composed of `cfg.py`, `cfg_base.py`, `netParams.py`, and `netParams_base.py`, defined an entire, interconnected thalamocortical network. For tuning the properties of a single cell type, this included many extraneous attributes and dependencies.

The new, improved files, `cfg_new.py` and `netParams_new.py`, are streamlined and standalone, containing only the necessary parameters for single-cell experiments.

---

## Configuration Simplification: `cfg_new.py`

`cfg_new.py` was created as a standalone configuration file, removing the dependencies on `cfg_base.py` and its associated JSON files. This was achieved by eliminating parameters related to full-network simulation.

### Removed Attributes for Simplification

The following parameters, present in the original `cfg`/`cfg_base` structure, were removed in `cfg_new.py` as they are irrelevant to single-cell tuning:

- **Multi-Population Definitions:** Removed lists defining all 40+ populations (`allpops`, `allCorticalPops`, `Epops`, `Ipops`, etc.). The new configuration only considers the population under study.
- **Network Connectivity Parameters:**
    - All network-wide connection flags (`addConn`, `addSubConn`, `wireCortex`).
    - All synaptic gain parameters for the full network (`EEGain`, `EIGain`, `IELayerGain`, `EICellTypeGain`, etc.).
    - All flags and parameters for thalamic, cortico-thalamic, and thalamo-cortical connections.
- **Complex External Inputs:** Removed definitions for complex inputs that are not used in single-cell f-I curve experiments, such as `ICThalInput` and `cochlearThalInput`.
- **Dynamic/Inherited Logic:** Removed logic that dynamically configured paths or loaded populations from external files (`pops_sz.csv`), as the setup is now static and explicit for a single population.

### Kept & Clarified Attributes

- **Core Run Parameters:** Essential parameters like `duration` and `dt` were kept.
- **Targeted Inputs:** The specific Ornstein-Uhlenbeck (OU) current parameters (`add_ou_current`, `OUamp`, etc.) and background `NetStim` rates (`bkg_r`, `bkg_w`) needed for the experiment were kept and are now primary components of the file.
- **Mechanism Modification:** A clear, self-contained structure `multiply_parameters` was defined to handle changes to cell mechanisms, replacing the less direct `mech_changes` dictionary.
- **Recording:** Recording is explicitly defined for the single population of interest (`IT5A`).

---

## Network Simplification: `netParams_new.py`

`netParams_new.py` is a self-contained network definition file. It replaces the previous system where `netParams.py` would dynamically modify the massive, full-network definition loaded from `netParams_base.py`.

### Removed Network Definitions

To focus only on the components needed for a single-cell experiment, the following were removed from the original `netParams`/`netParams_base` structure:

- **All Population Definitions Except One:** All `popParams` entries for the ~40 populations were removed, leaving only the definition for `IT5A`.
- **All Connectivity Rules:** The entire `connParams` dictionary, which contained hundreds of rules for wiring the full cortex and thalamus, was removed as connections are not needed for this tuning task.
- **Subcellular Synapse Rules:** The `subConnParams` dictionary, defining synaptic distributions, was removed.
- **Unused Cell Models:** The loading of numerous `cellParams` files for unused cell types was removed.
- **Complex Input Populations:** Definitions for input populations like `cochlea` and `IC` were removed.

### Kept and Made Explicit

The `netParams_new.py` file now explicitly and clearly defines only what is necessary:

- **Single Cell & Population:** It loads only the `IT5A_reduced_cellParams.json` and defines only the `IT5A` population.
- **Explicit Input Definition:**
    - The Ornstein-Uhlenbeck current is now explicitly defined as an `IClamp` source (`NoiseOU_source_POP`). This makes its implementation clear and self-contained, unlike the previous abstract implementation.
    - The background jitter is explicitly defined with a `NetStim` source (`bkg_src_POP`) and its corresponding target, including the required `AMPA` synaptic mechanism.
- **Self-Contained Logic:** The logic for modifying mechanism parameters is now a simple, local function (`multiply_parameters_func`) within the file, removing the need to reference other files.
