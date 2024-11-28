import numpy as np
from scipy.linalg import eigh
import logging

def t_music_time(IQ, num_sources, candidate_delays, sampling_frequency, num_taps, tap_spacing):
    """
    T-MUSIC algorithm using time diversity (temporal information).
    
    Parameters:
        IQ: np.ndarray
            Received IQ signal (1D array with complex samples).
        num_sources: int
            Number of sources.
        candidate_delays: np.ndarray
            Candidate delays (in seconds) to evaluate the pseudospectrum.
        sampling_frequency: float
            Sampling frequency of the signal (Hz).
        num_taps: int
            Number of temporal taps (virtual sensors).
        tap_spacing: int
            Spacing between taps (in samples).
    
    Returns:
        pseudospectrum: np.ndarray
            The T-MUSIC pseudospectrum for the candidate delays.
    """
    # Validate IQ signal length
    if len(IQ) < num_taps * tap_spacing:
        raise ValueError("IQ data is too short for the desired number of taps and spacing.")
    
    # Prepare data with temporal taps
    data = np.array([
        IQ[i: len(IQ) - (num_taps - 1) * tap_spacing + i] for i in range(0, num_taps * tap_spacing, tap_spacing)
    ])
    
    # Compute the covariance matrix of the data
    R = np.dot(data, data.conj().T) / data.shape[1]
    
    # Eigen-decomposition of the covariance matrix
    eigenvalues, eigenvectors = eigh(R)
    
    # Sort eigenvalues and eigenvectors
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Separate the signal and noise subspaces
    signal_subspace = eigenvectors[:, :num_sources]
    noise_subspace = eigenvectors[:, num_sources:]
    
    # Pseudospectrum initialization
    pseudospectrum = np.zeros_like(candidate_delays, dtype=np.float64)
    
    for i, delay in enumerate(candidate_delays):
        # Create a temporal steering vector for the delay
        steering_vector = np.exp(-1j * 2 * np.pi * np.arange(data.shape[0]) * delay * sampling_frequency)
        
        # Project the steering vector onto the noise subspace
        projection = np.dot(noise_subspace.conj().T, steering_vector)
        pseudospectrum[i] = 1 / np.linalg.norm(projection)
    
    return pseudospectrum


def RMSE(y_est, y_true):
    if np.isscalar(y_est) and np.isscalar(y_true):
        return abs(y_est - y_true)  # For scalars abs error = rmse
    y_est, y_true = np.array(y_est), np.array(y_true)
    if len(y_est) != len(y_true):
        logging.error(f"Length of estimated values and true values does not match: est={len(y_est)}, true={len(y_true)}")
        raise ValueError("The lengths of estimated and true values must be the same.")
    N = len(y_est)
    return np.sqrt(np.sum((y_est - y_true) ** 2) / N)



# Example Usage
if __name__ == "__main__":
    # Parameters
    num_samples = 80
    num_sources = 2
    sampling_frequency = 1e6  # 1 MHz
    
    # Simulated data (num_channels = temporal taps or virtual sensors)
    num_channels = 8
    data = np.random.randn(num_channels, num_samples) + 1j * np.random.randn(num_channels, num_samples)
    
    # Candidate delays (in seconds)
    candidate_delays = np.linspace(0, 1e-6, 500)  # Example delay range from 0 to 1 µs
    
    # Apply T-MUSIC with time diversity
    pseudospectrum = t_music_time(data, num_sources, candidate_delays, sampling_frequency)
    
    # Plot the pseudospectrum
    import matplotlib.pyplot as plt
    plt.plot(candidate_delays * 1e6, 10 * np.log10(pseudospectrum / np.max(pseudospectrum)))
    plt.title("T-MUSIC Pseudospectrum with Time Diversity")
    plt.xlabel("Delay (µs)")
    plt.ylabel("Spectrum (dB)")
    plt.grid()
    plt.savefig("test.png", dpi=400)
