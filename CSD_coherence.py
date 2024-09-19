import numpy as np
from scipy.signal import coherence
from netpyne import sim


def fitness_function(simulated_data, target_csd_profile, fs=1000):
    """
    Calculate the fitness score based on spectral coherence between simulated data and target CSD profile.

    Parameters:
    simulated_data (np.array): The simulated current source density data (2D array: electrodes x time).
    target_csd_profile (np.array): The target current source density profile (2D array: electrodes x time).
    fs (int): Sampling frequency in Hz.

    Returns:
    float: Fitness score (higher is better).
    """
    num_electrodes = simulated_data.shape[0]
    coherence_values = []

    for i in range(num_electrodes):
        # Ensure the data lengths match
        min_length = min(len(simulated_data[i]), len(target_csd_profile[i]))
        sim_data = simulated_data[i][:min_length]
        target_data = target_csd_profile[i][:min_length]

        # Compute spectral coherence
        f, Cxy = coherence(sim_data, target_data, fs=fs)

        # Store the mean coherence value for this electrode
        coherence_values.append(np.mean(Cxy))

    # Calculate the overall fitness score as the mean coherence value across all electrodes
    fitness_score = np.mean(coherence_values)

    return fitness_score

simulated_data = sim.loadAll('/Users/scoot/A1ProjData/A1_sim_data/L6ETune0801A/L6ETune0801A_0_0_0_0_0_0_data.pkl')
target_csd_profile = sim.loadAll()

fitness_score = fitness_function(simulated, target)
print(f"Fitness Score: {fitness_score}")