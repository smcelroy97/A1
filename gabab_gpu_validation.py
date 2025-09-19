import matplotlib.pyplot as plt
from neuron import h, gui

# Load both mechanisms
h('load_file("stdrun.hoc")')

# Create a section
soma = h.Section(name='soma')
soma.L = soma.diam = 20

# Insert both mechanisms at different locations
syn_orig = h.GABAB(0.3, sec=soma)  # original
syn_mod = h.GABAB_SM(0.7, sec=soma)  # modified (rename in mod file)

# Stimulus
stim = h.NetStim()
stim.number = 1
stim.start = 10

# Stimulus
stim = h.NetStim()
stim.number = 1
stim.start = 10

# NetCon for each synapse
nc_orig = h.NetCon(stim, syn_orig)
nc_mod = h.NetCon(stim, syn_mod)
nc_orig.weight[0] = 1
nc_mod.weight[0] = 1

# Record variables
t = h.Vector().record(h._ref_t)
i_orig = h.Vector().record(syn_orig._ref_i)
i_mod = h.Vector().record(syn_mod._ref_i)

# Run
h.finitialize(-65)
h.continuerun(1000)

# Plot
plt.figure(figsize=(8, 6))  # Increase the figure size
plt.plot(t, i_orig, label='Original')
plt.plot(t, i_mod, label='Modified')
plt.xlabel('Time (ms)')
plt.ylabel('Current (nA)')
plt.legend()
plt.tight_layout()  # Adjust layout to prevent label cutoff
plt.savefig('gabab_comparison.png')
