import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from itertools import combinations
from scipy.optimize import minimize

def ellipse_equation(x, h, k, a, b, theta):
    """Compute the implicit form of a rotated ellipse."""
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    x_rot = cos_t * (x[0] - h) + sin_t * (x[1] - k)
    y_rot = cos_t * (x[1] - k) - sin_t * (x[0] - h)
    return (x_rot / a)**2 + (y_rot / b)**2 - 1

def total_distance(x, ellipses):
    """Calculate the sum of squared distances from a point to multiple ellipses."""
    return np.sum([
        np.abs(ellipse_equation(x, h, k, a, b, theta))**2
        for h, k, a, b, theta in ellipses
    ])

def generate_ellipse_param(focal_1, focal_2, refl_total_distance):
    """Generate ellipse parameters based on device measurements."""
    focal_1, focal_2 = np.array(focal_1), np.array(focal_2)
    center = (focal_1 + focal_2) / 2
    direction = focal_1 - focal_2
    total_distance = refl_total_distance
    semi_major = total_distance / 2

    # Validate semi-major axis and calculate eccentricity
    if semi_major <= np.linalg.norm(direction) / 2:
        raise ValueError("Invalid semi-major axis: must be larger than half the focal distance.")

    #eccentricity = min((np.linalg.norm(direction) / 2) / semi_major, 1 - 1e-6)
    #semi_minor = semi_major * np.sqrt(1 - eccentricity**2)
    semi_minor = 1/2*np.sqrt(total_distance**2 - np.linalg.norm(direction)**2)
    angle = np.arctan2(direction[1], direction[0])
    return center[0], center[1], semi_major, semi_minor, angle

def find_closest_intersection(ellipses):
    """Find the closest intersection point to the ellipses."""
    initial_guess = [0, 0]
    result = minimize(total_distance, initial_guess, args=(ellipses,), method='BFGS')
    return result.x

def plot_ellipse(ax, ellipses, color, linestyle):
    """Plot ellipses on the provided axes."""
    for i, (h, k, a, b, theta) in enumerate(ellipses):
        ellipse_patch = Ellipse(
            (h, k), width=2 * a, height=2 * b, angle=np.degrees(theta),
            edgecolor=color, facecolor="none", linestyle=linestyle, linewidth=2
        )
        ax.add_patch(ellipse_patch)

    