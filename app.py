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
    #your_score = sum(user_scores[m] * weights.get(m, 0) for m in user_scores)
    ## the row needs to include the rank estimate using the your_score against other's 'weighted scores'.
    # going to exclude total_Score for now as we know that isn't necessarily accurate.

    # So with your_score included, we need to create a new weighted score column using the weighted_average() function.
    # Then we can re-rank those, and take the rank of our scenario - and this is the new estimated rank that needs to be displayed.

    # needs to be added to combined_df now
    initial_row_to_add = {
        'institition': 'You',
        **user_scores
    }

    combined_df = pd.concat([combined_df, pd.DataFrame([initial_row_to_add])], ignore_index=True)

    combined_df['New Weighted Score'] = combined_df[metric_cols].apply(lambda row: weighted_average(row, weights), axis=1)
    combined_df['scenario_rank'] = combined_df['New Weighted Score'].rank(method='min', ascending=False).astype(int)
                                          
    new_estimated_rank = combined_df.loc[combined_df['institution'] == 'You', 'scenario_rank'].iat[0]

    you_row = {
        'institution': 'You',
        'rank': new_estimated_rank
        #'total_score': your_score,
        **user_scores
    }
    combined_df = pd.concat([combined_df, pd.DataFrame([you_row])], ignore_index=True)

    combined_df.drop(['New Weighted Score', 'scenario_rank'], axis=1, inplace=True)

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

# Display on the right.
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



"""What we need to do - 
take the weighted score (calculated with the weighted total of the scores) - then re-rank - that should give us the new rank for 'You' - 
but obviously we'll then have to change some of the code above to effectively 'fake' the rank of the 'You' scenario - and to input it at that point - 
shifting those below it.


"""