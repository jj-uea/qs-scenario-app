## Handles reading and preparing data.

import pandas as pd

def load_qs_data(data_path="qs_data.csv", weights_path="qs_weightings.csv"):
    """Load QS data and normalize weights."""
    data = pd.read_csv(data_path, encoding='latin1')
    weights_df = pd.read_csv(weights_path, encoding='latin1')

    weights = weights_df.set_index("metric")["weight"].to_dict()
    total_weight = sum(weights.values())
    weights = {k: v / total_weight for k, v in weights.items()}

    return data, weights


def prepare_baseline(data, year=2026):
    """Prepare baseline QS data with total scores and metrics."""
    metrics_df = (
        data[data['year'] == year]
        .pivot_table(index='institution', columns='metric', values='score')
        .reset_index()
    )

    overall_df = (
        data[(data['year'] == year) & (data['metric'] == 'Overall')]
        [['institution', 'score']]
        .rename(columns={'score': 'total_score'})
    )

    combined_df = pd.merge(overall_df, metrics_df, on='institution', how='left')
    combined_df['rank'] = combined_df['total_score'].rank(method='min', ascending=False).astype(int)

    return combined_df
