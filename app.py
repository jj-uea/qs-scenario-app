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

# --- Prepare QS 2026 Table: Use original 'Overall' scores ---
qs_2026_overall = data[(data['year'] == 2026) & (data['metric'] == 'Overall')].copy()
qs_2026_overall = qs_2026_overall[['institution', 'score']].rename(columns={'score': 'total_score'})


# Prepare QS 2026 baseline table with total_score and metrics
qs_2026_metrics = data[data['year'] == 2026].pivot_table(index='institution', columns='metric', values='score').reset_index()
qs_2026_overall = data[(data['year'] == 2026) & (data['metric'] == 'Overall')][['institution', 'score']].rename(columns={'score': 'total_score'})

# Merge them into one baseline table
combined_df = pd.merge(qs_2026_overall, qs_2026_metrics, on='institution', how='left')

# If user submitted form, add their row
if submitted:
    your_score = sum(user_scores[m] * weights.get(m, 0) for m in user_scores)
    you_row = {
        'institution': 'You',
        'total_score': your_score,
        **user_scores
    }
    combined_df = pd.concat([combined_df, pd.DataFrame([you_row])], ignore_index=True)

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

# --- Display on the right ---
# with col2:
#     st.subheader("QS 2026 League Table (with Your Scenario if Submitted)")
    
#     # Ensure correct column order
#     display_cols = ['institution', 'total_score', 'rank'] + [m for m in metrics if m in pivot_display.columns]
#     pivot_display = pivot_display[display_cols]
    
#     st.dataframe(pivot_display.style.format(precision=2), use_container_width=True)

with col2:
    st.subheader("QS 2026 League Table (with Your Scenario if Submitted)")
    
    display_cols = ['institution', 'total_score', 'rank'] + [m for m in metrics if m in combined_df.columns]
    st.dataframe(combined_df[display_cols].style.format(precision=2), use_container_width=True)

# --- Your results below ---
if submitted:
    your_row = combined_df[combined_df['institution'] == 'You'].iloc[0]
    st.subheader("Your Results")
    st.markdown(f"**Total Weighted Score:** {your_row['total_score']:.2f}")
    st.markdown(f"**Overall Rank:** {your_row['rank']} of {len(combined_df)}")