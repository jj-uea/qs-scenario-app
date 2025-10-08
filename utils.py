import pandas as pd
import numpy as np
import streamlit as st

# --- Load data ---
@st.cache_data
def load_data():
    data = pd.read_csv("data/qs_data.csv", encoding='latin1')
    weights_df = pd.read_csv("data/qs_weightings.csv", encoding='latin1')
    weights = weights_df.set_index("metric")["weight"].to_dict()
    total_weight = sum(weights.values())
    weights = {k: v / total_weight for k, v in weights.items()}
    return data, weights


def prepare_baseline(data, year=2026):
    metrics = data[data["year"] == year].pivot_table(
        index="institution", columns="metric", values="score"
    ).reset_index()
    overall = (
        data[(data["year"] == year) & (data["metric"] == "Overall")]
        [["institution", "score"]]
        .rename(columns={"score": "total_score"})
    )
    combined = pd.merge(overall, metrics, on="institution", how="left")
    combined["rank"] = combined["total_score"].rank(method="min", ascending=False).astype(int)
    
    return combined


def weighted_average(row, weights_dict):
    values = row.values.astype(float)
    metric_names = row.index
    mask = ~np.isnan(values)

    if mask.sum() == 0:
        return np.nan  # skip if all values are NaN

    # Get the corresponding weights for the non-NaN metrics
    used_weights = np.array([weights_dict[metric] for metric in metric_names[mask]])
    used_weights = used_weights / used_weights.sum()  # normalize weights

    return np.dot(values[mask], used_weights)


metric_cols = [
    'Academic Reputation',
    'Citations per Faculty',
    'Employer Reputation',
    'Faculty Student Ratio',
    'Employment Outcomes',
    'International Faculty Ratio',
    'International Research Network',
    'International Student Ratio',
    'Sustainability',
    'International Student Diversity'
]