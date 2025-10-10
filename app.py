import streamlit as st
import pandas as pd
from config import uea_current_scores
from utils import *
from app_helpers import load_custom_css
from simulate import simulate_scenario

# Set page layout style.
st.set_page_config(layout="wide")
# Load custom CSS.
load_custom_css()

# Initialise logo columns
logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])

# with logo_col2:
#     st.image("img/uea3.png", use_container_width=False, width=220)
#     st.image("img/QS-ranking.jpg", use_container_width=False, width=220)

# --- logo (Option A: Streamlit columns) ---
with logo_col2:
    left, spacer, right = st.columns([1, 0.08, 1])  # spacer fraction controls gap
    with left:
        st.image("img/uea3.png", use_container_width=False, width=500)
    with right:
        st.image("img/QS-ranking.jpg", use_container_width=False, width=500)


# --- Load data ---
#@st.cache_data
data, weights = load_data()
metrics = list(weights.keys())

# --- Layout ---
st.title("UEA QS International League Table Scenario Tool")
st.divider()

col1, spacer, col2 = st.columns([10, 3, 20])

with col1:
    st.subheader("Adjust Your Metric Scores")
    st.markdown(
        """
        <div style="padding: 15px; background-color: #1a1c23; border-radius: 8px;">
        """,
        unsafe_allow_html=True
    )
    with st.form("score_form"):
        user_scores = {}
        for metric in metrics:
            weight_pct = weights.get(metric, 0) * 100
            user_scores[metric] = st.number_input(
                f"{metric} Score ({weight_pct:.0f}% Weighting)",
                min_value=0.0,
                max_value=100.0,
                value=uea_current_scores.get(metric, 50.0)
            )
        submitted = st.form_submit_button("Calculate")
    st.markdown("</div>", unsafe_allow_html=True)

combined_df = prepare_baseline_data(data, year=2026)

# get UEA origiinal row for later use.
uea_original_row = combined_df.loc[combined_df['institution'] == "The University of East Anglia"].copy()

# If user submitted form, add their new row
if submitted:
    #your_score = sum(user_scores[m] * weights.get(m, 0) for m in user_scores)

    # needs to be added to combined_df now
    initial_row_to_add = {
        'institution': 'You',
        **user_scores
    }

    scenario_total_score, new_estimated_rank = simulate_scenario(combined_df, initial_row_to_add, weights)

    # create our new row.
    you_row = {
        'institution': 'The University of East Anglia',
        'total_score': scenario_total_score,
        'rank': new_estimated_rank,
        **user_scores
    }

    print(f"TOTAL SCORE FOR UEA: {scenario_total_score}")

    # add new UEA results to the combined dataframe.
    for col, val in you_row.items():
        combined_df.loc[combined_df['institution'] == "The University of East Anglia", col] = val

    # Now re-rank fully for final table display
    combined_df['rank'] = combined_df['total_score'].rank(method='min', ascending=False).astype(int)

# Sort for display
combined_df = combined_df.sort_values(by='rank').reset_index(drop=True)

# Display on the right.
with col2:
    display_cols = ['institution', 'total_score', 'rank'] + [m for m in metrics if m in combined_df.columns]

    # Display UEA only table (for easy viewing).
    st.subheader("QS 2026 UEA's League Table Results (with Your Scenario if Submitted)")
    st.dataframe(combined_df.query("institution == 'The University of East Anglia'")[display_cols].style.apply(highlight_uea, axis=1).format(precision=2), 
                 use_container_width=True, hide_index=True)
    
    st.divider()

    # Display whole sector table (for detailed viewing).
    st.subheader("QS 2026 League Table (with Your Scenario if Submitted)")
    st.dataframe(combined_df[display_cols].style.apply(highlight_uea, axis=1).format(precision=2), 
                 use_container_width=True, hide_index=True)

    # Give some basic info of the scenario changes.
    if submitted:
        original_rank = int(uea_original_row['rank'].values[0])
        new_rank = new_estimated_rank
        rank_change = original_rank - new_rank
        st.divider()
        st.subheader("Scenario Impact for UEA")
        st.markdown(f"**Rank Change:** {rank_change:+} positions")
        
        for metric in user_scores:
            orig_score = float(uea_original_row[metric].values[0])
            new_score = float(user_scores[metric])
            diff = new_score - orig_score
            st.markdown(f"- **{metric}**: {orig_score:.1f} → {new_score:.1f} ({diff:+.1f})")
