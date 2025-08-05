import streamlit as st
import pandas as pd
from config import uea_current_scores

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

# --- Prepare QS 2026 Pivot Table (always shown on the right) ---
qs_2026 = data[data['year'] == 2026].copy()

pivot = qs_2026.pivot_table(index='institution', columns='metric', values='score', aggfunc='mean').fillna(0)

# Ensure all metrics exist as columns
for metric in metrics:
    if metric not in pivot.columns:
        pivot[metric] = 0

# --- Add user "You" row if submitted ---
if submitted:
    user_df = pd.DataFrame(user_scores, index=["You"])
    pivot = pd.concat([pivot, user_df])

# --- Compute total_score and rank ---
pivot['total_score'] = pivot[metrics].mul(pd.Series(weights)).sum(axis=1)
pivot['rank'] = pivot['total_score'].rank(method='min', ascending=False)

# Final formatting
pivot_display = pivot.reset_index()
pivot_display['rank'] = pivot_display['rank'].astype(int)
pivot_display = pivot_display[['institution', 'total_score', 'rank'] + metrics]
pivot_display = pivot_display.sort_values(by='rank').reset_index(drop=True)

# --- RIGHT: Table Display (always visible) ---
with col2:
    st.subheader("QS 2026 League Table (with Your Scenario if Submitted)")
    st.dataframe(pivot_display.style.format(precision=2), use_container_width=True)

# --- OPTIONAL: Show user summary if submitted ---
if submitted:
    your_score = pivot.loc["You", "total_score"]
    your_rank = int(pivot.loc["You", "rank"])
    
    st.subheader("Your Results")
    st.markdown(f"**Total Weighted Score:** {your_score:.2f}")
    st.markdown(f"**Overall Rank:** {your_rank} of {len(pivot)}")
