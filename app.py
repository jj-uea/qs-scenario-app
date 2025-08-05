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

# Create pivot of full dataset for display
pivot = data.pivot_table(index='institution', columns='metric', values='score', aggfunc='mean').fillna(0)
pivot.index.name = "institution"
pivot = pivot.reset_index()

# --- Layout ---
st.title("UEA QS International League Table Scenario Tool")

col1, col2 = st.columns([1, 2])  # Wider col2 for table

# --- LEFT: User Input Form ---
with col1:
    st.subheader("Enter Your Metric Scores")
    with st.form("score_form"):
        user_scores = {}
        for metric in metrics:
            default = uea_current_scores.get(metric, 50.0)
            user_scores[metric] = st.number_input(f"{metric} Score", min_value=0.0, max_value=100.0, value=default)
        submitted = st.form_submit_button("Calculate")

# --- RIGHT: League Table ---
# with col2:
#     st.subheader("Full League Table")

#     # If some metrics are missing in pivot (just in case), fill with 0
#     for metric in metrics:
#         if metric not in pivot.columns:
#             pivot[metric] = 0

#     pivot['total_score'] = pivot[metrics].mul(pd.Series(weights)).sum(axis=1)
#     pivot['rank'] = pivot['total_score'].rank(method='min', ascending=False)
#     pivot['rank'] = pivot['rank'].astype(int)

#     display_df = pivot[['institution', 'total_score', 'rank'] + metrics]
#     display_df = display_df.sort_values(by='rank')

#     st.dataframe(display_df.style.format(precision=2), use_container_width=True)


# --- Show user results only after form submission ---
if submitted:
    st.subheader("Your Results")

    # Filter to 2026 only (all metrics)
    qs_2026 = data[data['year'] == 2026].copy()

    # Create pivot from 2026 data: institution × metric
    pivot = qs_2026.pivot_table(index='institution', columns='metric', values='score', aggfunc='mean').fillna(0)
    
    # Append user to pivot
    user_df = pd.DataFrame(user_scores, index=['You'])
    #full_pivot = data.pivot_table(index='institution', columns='metric', values='score', aggfunc='mean').fillna(0)
    #full_pivot = pd.concat([full_pivot, user_df])
    pivot = pd.concat([pivot, user_df])
    
    # apply weights
    for metric in weights:
        if metric not in pivot.columns:
            pivot[metric] = 0
        
    pivot['total_score'] = pivot[metrics].mul(pd.Series(weights)).sum(axis=1)
    #full_pivot['total_score'] = full_pivot[metrics].mul(pd.Series(weights)).sum(axis=1)
    pivot['rank'] = pivot['total_score'].rank(method='min', ascending=False)
    
    your_score = pivot.loc['You', 'total_score']
    your_rank = int(pivot.loc['You', 'rank'])

    st.markdown(f"**Total Weighted Score:** {your_score:.2f}")
    st.markdown(f"**Overall Rank:** {your_rank} of {len(pivot)}")

    st.markdown(f"**Total Weighted Score:** {your_score:.2f}")
    st.markdown(f"**Overall Rank:** {your_rank} of {len(pivot)}")

    # Display full table including "You"
    display_df = pivot.reset_index()
    display_df['rank'] = display_df['rank'].astype(int)
    display_df = display_df[['institution', 'total_score', 'rank'] + metrics]  # show other metrics too
    display_df = display_df.sort_values(by='rank')

    st.subheader("Scenario League Table (with You)")
    st.dataframe(display_df.style.format(precision=2), use_container_width=True)