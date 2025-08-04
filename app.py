import streamlit as st
import pandas as pd
from config import uea_current_scores

# --- Load data ---
@st.cache_data
def load_data():
    data = pd.read_csv("qs_data.csv", encoding='latin1')
    weights_df = pd.read_csv("qs_weightings.csv", encoding='latin1')
    weights = weights_df.set_index("metric")["weight"].to_dict()
    weights = {k: v / sum(weights.values()) for k, v in weights.items()}  # Normalize
    return data, weights

data, weights = load_data()
metrics = list(weights.keys())

# --- Layout ---
st.title("UEA QS International League Table Scenario Tool")
st.write("Enter your scores for each metric (0–100) to simulate your institution's rank.")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Your Input Scores")
    user_scores = {}
    with st.form("score_form"):
        for metric in metrics:
            #user_scores[metric] = st.number_input(f"{metric}", min_value=0.0, max_value=100.0, value=50.0)
            
            default = uea_current_scores.get(metric, 50.0)
            user_scores[metric] = st.number_input(f"{metric}", min_value=0.0, max_value=100.0, value=default)

        submitted = st.form_submit_button("Calculate")

if submitted:
    # --- Calculate metric ranks ---
    st.header("Results")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Your Ranks by Metric")
        for metric, score in user_scores.items():
            metric_data = data[data['metric'] == metric].copy()
            metric_data = pd.concat([
                metric_data,
                pd.DataFrame([{'institution': 'You', 'metric': metric, 'score': score}])
            ], ignore_index=True)
            metric_data['rank'] = metric_data['score'].rank(method='min', ascending=False)
            your_rank = int(metric_data[metric_data['institution'] == 'You']['rank'].values[0])
            st.write(f"**{metric}**: Rank {your_rank} of {len(metric_data)}")

    # --- Pivot & weighted score ---
    pivot = data.pivot_table(index='institution', columns='metric', values='score').fillna(0)
    user_df = pd.DataFrame(user_scores, index=['You'])
    pivot = pd.concat([pivot, user_df])
    
    for metric in weights:
        if metric in pivot.columns:
            pivot[metric] = pivot[metric] * weights[metric]
        else:
            pivot[metric] = 0

    pivot['total_score'] = pivot[[m for m in weights]].sum(axis=1)
    pivot['rank'] = pivot['total_score'].rank(method='min', ascending=False)

    your_score = pivot.loc['You', 'total_score']
    your_rank = int(pivot.loc['You', 'rank'])

    with col1:
        st.subheader("Overall Result")
        st.write(f"**Total weighted score:** {your_score:.2f}")
        st.write(f"**Overall rank:** {your_rank} of {len(pivot)}")

    with col2:
        st.subheader("Full League Table")

        # Ensure all metric columns exist in pivot
        for metric in metrics:
            if metric not in pivot.columns:
                pivot[metric] = 0

        # Prepare display DataFrame
        display_df = pivot.reset_index()



        # Only use metrics that exist in the DataFrame
        existing_metrics = [m for m in metrics if m in display_df.columns]

        # Rebuild the display column list safely
        display_columns = ['institution', 'total_score', 'rank'] + existing_metrics

        # Now safely select the columns
        display_df = display_df[display_columns]

        # Build list of columns to show (only those that actually exist)
        #display_columns = ['institution', 'total_score', 'rank'] + [m for m in metrics if m in display_df.columns]

        # Reorder and display
        #display_df = display_df[display_columns]
        display_df = display_df.sort_values(by='rank')
        display_df['rank'] = display_df['rank'].astype(int)

        st.dataframe(display_df.style.format(precision=2), use_container_width=True)

