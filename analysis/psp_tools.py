import pickle
import os

batch_dir = '../simOutput/PSPTest/'

for file in os.listdir(batch_dir):
    if file.endswith('.pkl'):
        with open(batch_dir + file, 'rb') as f:
            sim_results = pickle.load(f)