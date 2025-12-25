from neuron import h
from netpyne import sim


def _collect_cell_gids():

    pc = sim.pc                       # NEURON ParallelContext

    # 1) Each rank finds the lowest / highest gid it owns for every population
    local_ranges = {}
    for popName, pop in sim.net.pops.items():
        gids_here = pop.cellGids      # rank-local list (may be empty)
        if gids_here:                 # some ranks don’t hold cells of this pop
            lo, hi = min(gids_here), max(gids_here)
            local_ranges[popName] = (lo, hi)

    # 2) Gather and merge to obtain the **global** (lo, hi) for every pop
    pop_gid_range = {}
    for part in pc.py_allgather(local_ranges):
        for name, (lo, hi) in part.items():
            if name in pop_gid_range:
                lo0, hi0 = pop_gid_range[name]
                pop_gid_range[name] = (min(lo0, lo), max(hi0, hi))
            else:
                pop_gid_range[name] = (lo, hi)

    # 3) Store once; a few dozen bytes per pop, shared by all your filters
    sim._pop_gid_range = pop_gid_range
