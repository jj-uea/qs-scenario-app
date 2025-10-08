import pandas as pd
import numpy as np
from typing import Dict
from utils import weighted_average, metric_cols


# def weighted_average(row, weights_dict):
#     values = row.values.astype(float)
#     metric_names = row.index
#     mask = ~np.isnan(values)

#     if mask.sum() == 0:
#         return np.nan  # skip if all values are NaN

#     # Get the corresponding weights for the non-NaN metrics
#     used_weights = np.array([weights_dict[metric] for metric in metric_names[mask]])
#     used_weights = used_weights / used_weights.sum()  # normalize weights

#     return np.dot(values[mask], used_weights)


# metric_cols = [
#     'Academic Reputation',
#     'Citations per Faculty',
#     'Employer Reputation',
#     'Faculty Student Ratio',
#     'Employment Outcomes',
#     'International Faculty Ratio',
#     'International Research Network',
#     'International Student Ratio',
#     'Sustainability',
#     'International Student Diversity'
# ]


def simulate_scenario(
    baseline_df: pd.DataFrame,
    weights: Dict[str, float],
    institution: str,
    new_scores: Dict[str, float],
):
    """
    Simulate a scenario where `institution` has its metric scores changed to `new_scores`.

    Returns:
        updated_df (pd.DataFrame): baseline_df with updated institution scores and re-ranked.
        result (dict): summary of new rank and total score for the institution.
    """
    df = baseline_df.copy()

    # Calculate new weighted score for the scenario
    df['Weighted_Score'] = df[metric_cols].apply(lambda r: weighted_average(r, weights), axis=1)

    # Replace institution metrics
    for metric, val in new_scores.items():
        df.loc[df['institution'] == institution, metric] = val

    # Recalculate weighted score for that institution
    df['Weighted_Score'] = df[metric_cols].apply(lambda r: weighted_average(r, weights), axis=1)

    # Rank
    df['rank'] = df['Weighted_Score'].rank(method='min', ascending=False).astype(int)

    inst_row = df.loc[df['institution'] == institution].iloc[0]
    result = {
        'institution': institution,
        'new_rank': int(inst_row['rank']),
        'new_total_score': float(inst_row['Weighted_Score']),
    }

    return df.sort_values('rank'), result
