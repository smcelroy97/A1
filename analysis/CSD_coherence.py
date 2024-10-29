import numpy as np
from scipy.signal import coherence
from netpyne import sim
import ot

def fitness_functionSCI(simulated_data, target_csd_profile, fs=20000):
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

def fitness_functionPOT(simulated_data, target_csd_profile):
    """
    Calculate the fitness score based on Wasserstein distance between simulated data and target CSD profile.

    Parameters:
    simulated_data (np.array): The simulated current source density data (2D array: electrodes x time).
    target_csd_profile (np.array): The target current source density profile (2D array: electrodes x time).

    Returns:
    float: Fitness score (lower is better).
    """
    num_electrodes = simulated_data.shape[0]
    wasserstein_distances = []

    for i in range(num_electrodes):
        # Ensure the data lengths match
        min_length = min(len(simulated_data[i]), len(target_csd_profile[i]))
        sim_data = simulated_data[i][:min_length]
        target_data = target_csd_profile[i][:min_length]

        # Compute Wasserstein distance
        distance = ot.wasserstein_1d(sim_data, target_data)
        wasserstein_distances.append(distance)

    # Calculate the overall fitness score as the mean Wasserstein distance across all electrodes
    fitness_score = np.mean(wasserstein_distances)

    return fitness_score


sim.initialize()
sim.loadAll('/Users/scoot/A1ProjData/A1_sim_data/L4GainTune0809/L4GainTune0809_0_0_0_0_data.pkl')
simCSD = sim.analysis.prepareCSD(timeRange = [5000, 5200])
# sim.plotting.plotCSD(timeRange = [5000, 5200], saveFig = '/Users/scoot/A1ProjData/A1_figs/SIMfigs/simCSDtest.png')

sim.initialize()
sim.loadAll('/Users/scoot/A1ProjData/A1_sim_data/v34_batch56_0_0_data.pkl')
targetCSD = sim.analysis.prepareCSD(timeRange=[3400, 3600])
# sim.plotting.plotCSD(timeRange = [3400, 3600], saveFig = '/Users/scoot/A1ProjData/A1_figs/SIMfigs/targetCSDtest.png')

fitness_scoreSCI = fitness_functionSCI(targetCSD[0], targetCSD[0])
fitness_scorePOT = fitness_functionPOT(targetCSD[0], targetCSD[0])

print(f"Fitness Score, Spectral Coherence: {fitness_scoreSCI}")
print(f"Fitness Score, Wasserstein Distance: {fitness_scorePOT}")