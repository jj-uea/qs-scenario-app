import streamlit as st
import pandas as pd
from config import uea_current_scores
from utils import *

# --- Load data ---
@st.cache_data
def load_data():
    data = pd.read_csv("qs_data.csv", encoding='latin1')
    weights_df = pd.read_csv("qs_weightings.csv", encoding='latin1')
    weights = weights_df.set_index("metric")["weight"].to_dict()
    total_weight = sum(weights.values())
    weights = {k: v / total_weight for k, v in weights.items()}
    return data, weights

data, weights = load_data()
metrics = list(weights.keys())

# --- Layout ---
st.title("UEA QS International League Table Scenario Tool")


"""

"""

col1, col2 = st.columns([1, 2])

# --- LEFT: User Inputs ---
with col1:
    st.subheader("Adjust Your Metric Scores")
    with st.form("score_form"):
        user_scores = {
            metric: st.number_input(
                f"{metric} Score",
                min_value=0.0,
                max_value=100.0,
                value=uea_current_scores.get(metric, 50.0)
            )
            for metric in metrics
        }
        submitted = st.form_submit_button("Calculate")

# --- Prepare QS 2026 Table: Use original 'Overall' scores ---
qs_2026_overall = data[(data['year'] == 2026) & (data['metric'] == 'Overall')].copy()
qs_2026_overall = qs_2026_overall[['institution', 'score']].rename(columns={'score': 'total_score'})


# Prepare QS 2026 baseline table with total_score and metrics
qs_2026_metrics = data[data['year'] == 2026].pivot_table(index='institution', columns='metric', values='score').reset_index()
qs_2026_overall = data[(data['year'] == 2026) & (data['metric'] == 'Overall')][['institution', 'score']].rename(columns={'score': 'total_score'})

# Merge them into one baseline table
combined_df = pd.merge(qs_2026_overall, qs_2026_metrics, on='institution', how='left')

# get UEA origiinal row for later use.
uea_original_row = combined_df.loc[combined_df['institution'] == "The University of East Anglia"].copy()

# If user submitted form, add their row
if submitted:
    #your_score = sum(user_scores[m] * weights.get(m, 0) for m in user_scores)

    # needs to be added to combined_df now
    initial_row_to_add = {
        'institution': 'You',
        **user_scores
    }

    combined_df_copy = combined_df.copy()
    combined_df_copy = pd.concat([combined_df_copy, pd.DataFrame([initial_row_to_add])], ignore_index=True)

    combined_df_copy['New Weighted Score'] = combined_df_copy[metric_cols].apply(
        lambda row: weighted_average(row, weights), axis=1
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

    you_row = {
        'institution': 'The University of East Anglia',
        'total_score': scenario_total_score,
        'rank': new_estimated_rank,
        **user_scores
    }

    print(f"TOTALSCORE FOR UEA: {scenario_total_score}")

    # Append to real combined_df
    #combined_df = pd.concat([combined_df, pd.DataFrame([you_row])], ignore_index=True)

    # add new UEA results.
    combined_df.loc[combined_df['institution'] == "The University of East Anglia", you_row.keys()] = pd.Series(you_row)

    # Now re-rank fully for final table display
    combined_df['rank'] = combined_df['total_score'].rank(method='min', ascending=False).astype(int)


# Rank the full combined table
combined_df['rank'] = combined_df['total_score'].rank(method='min', ascending=False).astype(int)

# Sort for display
combined_df = combined_df.sort_values(by='rank').reset_index(drop=True)


# --- Rank all by total_score ---
qs_2026_overall['rank'] = qs_2026_overall['total_score'].rank(method='min', ascending=False).astype(int)

# --- Optional: Merge back individual metric scores for display ---
qs_2026_metrics = data[data['year'] == 2026].pivot_table(index='institution', columns='metric', values='score').reset_index()

# Merge only for display purposes
pivot_display = pd.merge(qs_2026_overall, qs_2026_metrics, on='institution', how='left')

# Final sort
pivot_display = pivot_display.sort_values(by='rank').reset_index(drop=True)

def highlight_uea(row):
    color = 'background-color: lightyellow' if row['institution'] == "The University of East Anglia" else ''
    return [color] * len(row)

# Display on the right.
with col2:
    st.subheader("QS 2026 League Table (with Your Scenario if Submitted)")
    
    display_cols = ['institution', 'total_score', 'rank'] + [m for m in metrics if m in combined_df.columns]
    #st.dataframe(combined_df[display_cols].style.format(precision=2), use_container_width=True)
    st.dataframe(combined_df.style.apply(highlight_uea, axis=1).format(precision=2), use_container_width=True)


# --- Your results below ---
# if submitted:
#     your_row = combined_df[combined_df['institution'] == 'You'].iloc[0]
#     st.subheader("Your Results")
#     st.markdown(f"**Total Weighted Score:** {your_row['total_score']:.2f}")
#     st.markdown(f"**Overall Rank:** {your_row['rank']} of {len(combined_df)}")

if submitted:
    original_rank = int(uea_original_row['rank'].values[0])
    new_rank = new_estimated_rank
    rank_change = original_rank - new_rank  # positive = moved up
    
    st.subheader("Scenario Impact for UEA")
    st.markdown(f"**Rank Change:** {rank_change:+} positions")
    
    for metric in user_scores:
        orig_score = float(uea_original_row[metric].values[0])
        new_score = float(user_scores[metric])
        diff = new_score - orig_score
        st.markdown(f"- **{metric}**: {orig_score:.1f} → {new_score:.1f} ({diff:+.1f})")
