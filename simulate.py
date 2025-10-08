import pandas as pd
import numpy as np
from utils import weighted_average

def simulate_scenario(df, weights, institution, new_scores):
    df = df.copy()
    for metric, val in new_scores.items():
        if metric not in df.columns:
            df[metric] = np.nan
        df.loc[df["institution"] == institution, metric] = val

    metric_cols = [m for m in weights if m in df.columns]
    df["Weighted_Score"] = df[metric_cols].apply(lambda r: weighted_average(r, weights), axis=1)

    df["rank"] = df["Weighted_Score"].rank(method="min", ascending=False).astype(int)
    inst_row = df.loc[df["institution"] == institution].iloc[0]
    return df, int(inst_row["rank"]), float(inst_row["Weighted_Score"])