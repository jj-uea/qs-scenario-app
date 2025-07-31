import streamlit as st
import pandas as pd

# --- Load data ---
@st.cache_data
def load_data():
    data = pd.read_csv("qs_data.csv", encoding='utf-8')
    weights_df = pd.read_csv("qs_weightings.csv", encoding='utf-8')
    weights = weights_df.set_index("metric")["weight"].to_dict()
    # Normalize weights to sum to 1 (if needed)
    total_weight = sum(weights.values())
    weights = {k: v / total_weight for k, v in weights.items()}
    return data, weights

data, weights = load_data()
metrics = list(weights.keys())

# --- Title & Instructions ---
st.title("University League Table Scenario Tool")
st.write("Enter your scores for each metric (0–100) to see where you'd rank.")

# --- User Input ---
user_scores = {}
with st.form("score_form"):
    for metric in metrics:
        user_scores[metric] = st.number_input(f"{metric} Score", min_value=0.0, max_value=100.0, value=50.0)
    submitted = st.form_submit_button("Calculate")

if submitted:
    # --- Show per-metric rank ---
    st.header("Your Ranks by Metric")
    for metric, score in user_scores.items():
        metric_data = data[data['metric'] == metric].copy()
        metric_data = pd.concat([
            metric_data,
            pd.DataFrame([{'institution': 'You', 'metric': metric, 'score': score}])
        ], ignore_index=True)
        metric_data['rank'] = metric_data['score'].rank(method='min', ascending=False)
        your_rank = int(metric_data[metric_data['institution'] == 'You']['rank'].values[0])
        st.write(f"**{metric}**: Rank {your_rank} of {len(metric_data)}")

    # --- Calculate weighted overall score ---
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

    # --- Show results ---
    st.header("Overall Weighted Result")
    st.write(f"**Your total weighted score:** {your_score:.2f}")
    st.write(f"**Your overall rank:** {your_rank} of {len(pivot)}")
