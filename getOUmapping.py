import pandas as pd
import numpy as np

# Load the CSV data
df = pd.read_csv('/Users/scoot/A1ProjData/A1_sim_data/v45_batch3.csv')

# Extract the unique OUamp and OUvar values from the headers
ouamp_values = sorted(set(float(col.split('_')[1]) for col in df.columns if col.startswith('OUamp')))
ouvar_values = sorted(set(float(col.split('_')[3]) for col in df.columns if col.startswith('OUamp')))

# Create a dictionary to store matrices for each population
population_matrices = {pop: np.zeros((len(ouamp_values), len(ouvar_values))) for pop in df.index}

# Populate the matrices with the corresponding values
for col in df.columns:
    if col.startswith('OUamp'):
        ouamp, ouvar = map(float, col.split('_')[1::2])
        ouamp_idx = ouamp_values.index(ouamp)
        ouvar_idx = ouvar_values.index(ouvar)
        for pop in df.index:
            population_matrices[pop][ouamp_idx, ouvar_idx] = df.at[pop, col]

# Example: Access the matrix for a specific population
# population = 'population_name'
# matrix = population_matrices[population]
# print(matrix)