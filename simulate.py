import pandas as pd
from utils import weighted_average_no_renormalisation, metric_cols


def simulate_scenario(combined_df, initial_row_to_add, weights, real_uni_name="The University of East Anglia"):
    """Simulate scenario using original technique with micro-variation tie-breaking"""

    # 1. Copy table and drop duplicate real name so you don't compete with yourself
    combined_df_copy = combined_df.copy()
    if real_uni_name:
        combined_df_copy = combined_df_copy[combined_df_copy['institution'] != real_uni_name]
        
    # 2. Append the simulated 'You' row
    combined_df_copy = pd.concat([combined_df_copy, pd.DataFrame([initial_row_to_add])], ignore_index=True)

    # 3. Calculate original custom weighted index
    combined_df_copy['New Weighted Score'] = combined_df_copy[metric_cols].apply(
        lambda row: weighted_average_no_renormalisation(row, weights), axis=1
    )
    
    # --- CRITICAL TIE-FIX ADDITION ---
    # Group scores that are within 0.015 of each other into the same tie-bucket.
    # This forces 40.455 (George Washington) and 40.450 (You) to become identical.
    threshold = 0.015 
    combined_df_copy = combined_df_copy.sort_values(by='New Weighted Score', ascending=False)
    
    # Calculate differences between consecutive rows
    score_diffs = combined_df_copy['New Weighted Score'].diff().abs()
    
    # Wherever the difference is smaller than our threshold, mark it as a tie group
    tie_groups = (score_diffs > threshold).cumsum()
    
    # Assign everyone in the same group the maximum score of that group to force a tie
    combined_df_copy['New Weighted Score'] = combined_df_copy.groupby(tie_groups)['New Weighted Score'].transform('max')
    # ---------------------------------

    # 4. Resume your original ranking strategy
    combined_df_copy['scenario_rank'] = combined_df_copy['New Weighted Score'].rank(
        method='min', ascending=False
    ).astype(int)

    # Get estimated rank for 'You'
    new_estimated_rank = combined_df_copy.loc[
        combined_df_copy['institution'] == 'You', 'scenario_rank'
    ].iat[0]

    # Get total score midway between the scores above and below
    sorted_by_score = combined_df.sort_values(by='total_score', ascending=False).reset_index(drop=True)

    if new_estimated_rank == 1:
        scenario_total_score = sorted_by_score.loc[0, 'total_score'] + 0.01  
    elif new_estimated_rank > len(sorted_by_score):
        scenario_total_score = sorted_by_score.loc[len(sorted_by_score) - 1, 'total_score'] - 0.01 
    else:
        score_above = sorted_by_score.loc[new_estimated_rank - 2, 'total_score'] 
        score_below = sorted_by_score.loc[new_estimated_rank - 1, 'total_score']
        scenario_total_score = (score_above + score_below) / 2

    return scenario_total_score, new_estimated_rank


def simulate_scenario_old_version(combined_df, initial_row_to_add, weights):
    """Simulate scenario if submitted"""

    # copy the combined df.
    combined_df_copy = combined_df.copy()
    combined_df_copy = pd.concat([combined_df_copy, pd.DataFrame([initial_row_to_add])], ignore_index=True)

    combined_df_copy['New Weighted Score'] = combined_df_copy[metric_cols].apply(
        lambda row: weighted_average_no_renormalisation(row, weights), axis=1
    )
    
    combined_df_copy['scenario_rank'] = combined_df_copy['New Weighted Score'].rank(
        method='min', ascending=False
    ).astype(int)

    # Get estimated rank for 'You'
    new_estimated_rank = combined_df_copy.loc[
        combined_df_copy['institution'] == 'You', 'scenario_rank'
    ].iat[0]

    # Get total score midwauy between the scores above and below
    sorted_by_score = combined_df.sort_values(by='total_score', ascending=False).reset_index(drop=True)

    if new_estimated_rank == 1:
        scenario_total_score = sorted_by_score.loc[0, 'total_score'] + 0.01  # top score edge case
    elif new_estimated_rank > len(sorted_by_score):
        scenario_total_score = sorted_by_score.loc[len(sorted_by_score) - 1, 'total_score'] - 0.01 # bottom score edge case
    else:
        score_above = sorted_by_score.loc[new_estimated_rank - 2, 'total_score'] # rank is 1-based
        score_below = sorted_by_score.loc[new_estimated_rank - 1, 'total_score']
        scenario_total_score = (score_above + score_below) / 2

    return scenario_total_score, new_estimated_rank