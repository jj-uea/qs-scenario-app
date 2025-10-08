import streamlit as st
import pandas as pd
from config import uea_current_scores
from utils import *
from simulate import *
from app_helpers import *

st.set_page_config(layout="wide")
load_custom_css()

logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])

with logo_col2:
    st.image("uea3.png", use_container_width=False, width=220)

st.markdown(
    """
    <style>
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
    }
    [data-testid="stImage"] img {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --- Layout ---
st.title("UEA QS International League Table Scenario Tool")

# Load and prepare data
data, weights = load_data()
baseline = prepare_baseline(data)

metrics = list(weights.keys())

# --- UI form ---
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

# --- Simulation ---

combined_df = baseline.copy()
# get UEA origiinal row for later use.
uea_original_row = combined_df.loc[combined_df['institution'] == "The University of East Anglia"].copy()

if submitted:
    combined_df, new_rank, new_score = simulate_scenario(
        combined_df, weights, "The University of East Anglia", user_scores
    )

# --- Display ---
with col2:
    st.subheader("QS 2026 Results (with Scenario if Submitted)")
    st.dataframe(
        combined_df.style.apply(highlight_uea, axis=1).format(precision=2),
        use_container_width=True,
        hide_index=True
    )

    if submitted:
        orig_rank = int(uea_original_row["rank"].values[0])
        st.subheader("Scenario Impact for UEA")
        st.markdown(f"**Rank Change:** {orig_rank - new_rank:+} positions")


###########################