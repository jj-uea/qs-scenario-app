import pandas as pd
import numpy as np

def weighted_average(row, weights_dict):
    values = row.values.astype(float)
    metric_names = row.index
    mask = ~np.isnan(values)

    if mask.sum() == 0:
        return np.nan  # skip if all values are NaN

    # Get the corresponding weights for the non-NaN metrics
    used_weights = np.array([weights_dict[metric] for metric in metric_names[mask]])
    used_weights = used_weights / used_weights.sum()  # normalize weights

    return np.dot(values[mask], used_weights)


metric_cols = [
    'Academic Reputation',
    'Citations per Faculty',
    'Employer Reputation',
    'Faculty Student Ratio',
    'Employment Outcomes',
    'International Faculty Ratio',
    'International Research Network',
    'International Student Ratio',
    'Sustainability',
    'International Student Diversity'
]