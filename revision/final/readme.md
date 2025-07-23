
- Difference between the versions:
    - "samn" - samn branch of the A1 NKI repo (commit: ca5f892)
    - "ouinp" - ou-griNN branch of A1_OUinp repo (commit: f14fd88)

- What changes I explored:
    - Ignored IC, cochlea, background, and stimuli
    - Listed the gain names, without values (as we will remove them anyway)
    - Listed the wmat elements that were changed directly (not via gains), without values
    - Listed other important changes with old/new values

- **Very brief summary of the changes**
    - Cell params: TC, ITC, ITS4
    - Gains (didn't explore the exact values)
    - synMechWeightFactor: SOM->Cortex, ThalI->ThalE
    - Distance-dependence: added for TI and IRE conns
    - popParams['ITS4']['cellType']: ITS4 replaced by IT
    - wmat entries related to L2/3 (from "v34_batch25/trial_2142/trial_2142_cfg.json")

- **diff_notes.md** - summary of the changes
    - *cells* - changes in the "cells/" folder
    - *cfg* - changes in the cfg object (used in sim.initialize)
    - *netParams* - additional changes in the netParams object not derived from the cfg object

- Detailed difference info:
    - **cfg_diff.json** - detailed info on the difference between cfg objects
    - **netpar_diff.json** - detailed info on the difference between netParams objects
        Note that it contains ALL differences, including those derived from cfg (e.g. weight changes caused by gain changes).

- **gains_wfactors_samn.md** - lists of all gains and weight fractions for every conn type

- Stored cfg and netParams objects used in sim.initialize():
    - **cfg_samn.json** - cfg object, "samn" version
    - **cfg_ouinp.json** - cfg object, "ouinp" version
    - **netParams_samn.json** - netParams object, "samn" version
    - **netParams_ouinp.json** - netParams object, "ouinp" version

- **cfg_sources_samn.md** - origins of each param contained in the cfg object ("samn" version):
    - *sim.json* (dconf)
    - *data/v34_batch25/trial_2142/trial_2142_cfg.json* (cfgLoad)
    - Hardcoded in *sim.py*
- **netpar_sources_samn.md** - origins of params that affect netParams but are not in cfg ("samn" version):
    - *sim.json* (dconf)

