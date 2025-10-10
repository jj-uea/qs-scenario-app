# chart.py
import plotly.graph_objects as go

def scenario_comparison_chart(metrics, original_scores, new_scores):
    """
    Returns a Plotly bar chart comparing original vs new scores for each metric.
    """
    fig = go.Figure()

    # Original scores
    fig.add_trace(go.Bar(
        x=metrics,
        y=original_scores,
        name="Original Score",
        marker_color="#565869"
    ))

    # New scores
    fig.add_trace(go.Bar(
        x=metrics,
        y=new_scores,
        name="New Score",
        marker_color="#00b4d8"
    ))

    fig.update_layout(
        barmode='group',
        title="Metric Comparison: Original vs Scenario Scores",
        xaxis_title="Metric",
        yaxis_title="Score",
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        #font=dict(color="#fafafa"),
        font=dict(color="#ffffff"),  # <-- Force white text always
            xaxis=dict(
            tickfont=dict(color="#ffffff"),
            #titlefont=dict(color="#ffffff"),
            gridcolor="#2a2d35",
        ),
        yaxis=dict(
            tickfont=dict(color="#ffffff"),
            #titlefont=dict(color="#ffffff"),
            gridcolor="#2a2d35",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#ffffff")  # <-- White legend labels too
        )
    )

    return fig


def basic_metrics_chart(metrics, original_scores):
    """
    Returns a Plotly bar chart comparing original vs new scores for each metric.
    """
    fig = go.Figure()

    # Original scores
    fig.add_trace(go.Bar(
        x=metrics,
        y=original_scores,
        name="Original Score",
        marker_color="#565869"
    ))

    fig.update_layout(
        barmode='group',
        title="UEA QS Metric Scores",
        xaxis_title="Metric",
        yaxis_title="Score",
        plot_bgcolor="#0e1117",
        paper_bgcolor="#0e1117",
        font=dict(color="#fafafa"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    return fig
