from lfpykit.eegmegcalc import NYHeadModel
import os
import matplotlib
matplotlib.use("MacOSX")
from matplotlib import pyplot as plt

nyhead = NYHeadModel(nyhead_file=os.getenv('NP_LFPYKIT_HEAD_FILE', None))
nyhead.set_dipole_pos([ -39.74573803, -21.57684261, 7.82510972])
M = nyhead.get_transformation_matrix()

# idx, lead = enumerate(nyhead.lead_field)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')
# for i in range len(nyhead.elecs):
ax.scatter(nyhead.elecs[0], nyhead.elecs[1], nyhead.elecs[2], c='r')
ax.scatter(-39.74573803, -21.57684261, 7.82510972, c='b')
# plt.savefig('/Users/scottmcelroy/Desktop/headFig.png')
plt.show()
# ax.scatter(nyhead.lead_field)
# # ax.scatter(idx)