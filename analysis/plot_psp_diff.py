import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

wo_gain = pd.read_csv('/Users/scoot/A1ProjData/A1_sim_data/v45_batch23/pop_psps.csv')

w_gain = pd.read_csv('/Users/scoot/A1ProjData/A1_sim_data/v45_batch24/pop_psps.csv')


merged = pd.merge(
    wo_gain,
    w_gain,
    on=['pop', 'prePop', 'syn_type'],
    suffixes=('_wo', '_w')
)

merged['amplitude_diff'] = merged['psp_w'] - merged['psp_wo']

for syn_type in ['E', 'I']:
    subset = merged[merged['syn_type'] == syn_type]
    heatmap_data = subset.pivot(index='pop', columns='prePop', values='amplitude_diff').fillna(0.0)
    plt.figure(figsize=(10, 8))
    sns.heatmap(heatmap_data, annot=False, cmap='viridis', center=0)
    plt.title(f'Amplitude Difference Heatmap (syn_type={syn_type})')
    plt.xlabel('prePop')
    plt.ylabel('pop')
    plt.show()