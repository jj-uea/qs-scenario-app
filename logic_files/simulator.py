import pandas as pd
import numpy as np
from typing import Dict
from utils import weighted_average, metric_cols


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
