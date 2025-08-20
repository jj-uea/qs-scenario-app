import streamlit as st
import pandas as pd
from config import uea_current_scores
from utils import *

st.set_page_config(layout="wide")
logo_col1, logo_col2, logo_col3 = st.columns([1, 2, 1])
#with logo_col2:
#    st.image("uea3.png", width=220)  # or use_container_width=True

st.markdown(
    """
    <style>
    /* General background & text */
    body, .stApp {
        background-color: #202225;  /* soft-dark */
        color: #f0f0f0;
    }

    /* Headers */
    h1, h2, h3, h4, h5, h6, .stMarkdown, .stSubheader, .stTitle {
        color: #ffffff !important;
    }

    /* Dataframes and tables */
    .stDataFrame, .stTable {
        background-color: #2c2f33 !important;
        color: #f0f0f0 !important;
        border-radius: 6px;
    }
    table {
        background-color: #2c2f33 !important;
        color: #f0f0f0 !important;
    }
    th {
        background-color: #23272a !important;
        color: #ffffff !important;
    }
    td {
        color: #e4e6eb !important;
    }

    /* Input fields */
    .stTextInput input, .stNumberInput input, .stSelectbox div, .stMultiSelect div, .stDateInput input {
        background-color: #2c2f33 !important;
        color: #f0f0f0 !important;
        border-radius: 4px;
        border: 1px solid #444;
    }

    /* Buttons */
    button, .stButton>button {
        background-color: #5865f2 !important; /* UEA-friendly purple/blue accent */
        color: white !important;
        border-radius: 6px;
        border: none;
    }
    button:hover, .stButton>button:hover {
        background-color: #4752c4 !important;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #2c2f33 !important;
        color: #f0f0f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# with logo_col2:
#     st.markdown(
#         """
#         <div style="text-align: center;">
#             <img src="uea3.png" style="max-width: 80%; height: auto;">
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

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

col1, spacer, col2 = st.columns([10, 3, 20])

# --- LEFT: User Inputs ---
# with col1:
#     st.subheader("Adjust Your Metric Scores")
#     with st.form("score_form"):
#         user_scores = {
#             metric: st.number_input(
#                 f"{metric} Score",
#                 min_value=0.0,
#                 max_value=100.0,
#                 value=uea_current_scores.get(metric, 50.0)
#             )
#             for metric in metrics
#         }
#         submitted = st.form_submit_button("Calculate")

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

# --- Prepare QS 2026 Table: Use original 'Overall' scores ---
#qs_2026_overall = data[(data['year'] == 2026) & (data['metric'] == 'Overall')].copy()
#qs_2026_overall = qs_2026_overall[['institution', 'score']].rename(columns={'score': 'total_score'})


# Prepare QS 2026 baseline table with total_score and metrics
qs_2026_metrics = data[data['year'] == 2026].pivot_table(index='institution', columns='metric', values='score').reset_index()
qs_2026_overall = data[(data['year'] == 2026) & (data['metric'] == 'Overall')][['institution', 'score']].rename(columns={'score': 'total_score'})

# Merge them into one baseline table
combined_df = pd.merge(qs_2026_overall, qs_2026_metrics, on='institution', how='left')

# Rank the full combined table
combined_df['rank'] = combined_df['total_score'].rank(method='min', ascending=False).astype(int)

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
    #combined_df.loc[combined_df['institution'] == "The University of East Anglia", you_row.keys()] = pd.Series(you_row)
    for col, val in you_row.items():
        combined_df.loc[combined_df['institution'] == "The University of East Anglia", col] = val

    # Now re-rank fully for final table display
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

# def highlight_uea(row):
#     color = 'background-color: darkblue' if row['institution'] == "The University of East Anglia" else ''
#     return [color] * len(row)

def highlight_uea(row):
    if row['institution'] == "The University of East Anglia":
        return ['background-color: gold; color: black; font-weight: bold'] * len(row)
    else:
        return [''] * len(row)

# Display on the right.
with col2:
    display_cols = ['institution', 'total_score', 'rank'] + [m for m in metrics if m in combined_df.columns]

    st.subheader("QS 2026 UEA's League Table Results (with Your Scenario if Submitted)")
    st.dataframe(combined_df.query("institution == 'The University of East Anglia'")[display_cols].style.apply(highlight_uea, axis=1).format(precision=2), 
                 use_container_width=True, hide_index=True)

    st.subheader("QS 2026 League Table (with Your Scenario if Submitted)")
    st.dataframe(combined_df[display_cols].style.apply(highlight_uea, axis=1).format(precision=2), 
                 use_container_width=True, hide_index=True)


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
