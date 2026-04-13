import pandas as pd
import pytest

from core.preprocessing import preprocess_comments
from core.trend_analysis import (
    build_valid_topics_df,
    add_month_column,
    attach_time_labels,
)
from core.visualization import (
    build_google_trends_style_chart,
    build_topic_distribution_bar,
)


@pytest.mark.integration
def test_preprocessing_and_trend_pipeline_integration():
    df = pd.DataFrame({
        "text": [
            "The economy is getting worse because of inflation and markets",
            "The team won the football match after a strong performance",
        ],
        "date": pd.to_datetime(["2024-01-10", "2024-01-20"]),
        "post_id": [1, 1],
    })

    clean_df = preprocess_comments(df, text_col="text", drop_duplicates=False)
    assert not clean_df.empty

    clean_df = clean_df.copy()
    clean_df["topic"] = [0] * len(clean_df)

    df_valid = build_valid_topics_df(clean_df, valid_topics=[0])
    assert not df_valid.empty
    assert "topic" in df_valid.columns

    df_valid = add_month_column(df_valid)
    assert "month" in df_valid.columns
    assert df_valid["month"].iloc[0] == "2024-01"

    topics_over_time = pd.DataFrame({
        "Timestamp": ["2024-01"],
        "Topic": [0],
        "Frequency": [len(df_valid)],
    })

    topic_info_labeled = pd.DataFrame({
        "Topic": [0],
        "CustomName": ["Economy"],
    })

    labeled = attach_time_labels(topics_over_time, topic_info_labeled)
    assert "topic_label" in labeled.columns
    assert labeled["topic_label"].iloc[0] == "Economy"


@pytest.mark.integration
def test_visualization_google_trends_chart_integration():
    topics_over_time = pd.DataFrame({
        "Timestamp": ["2024-01", "2024-02", "2024-03"],
        "Topic": [0, 0, 0],
        "Frequency": [10, 20, 15],
        "topic_label": ["Economy", "Economy", "Economy"],
    })

    fig = build_google_trends_style_chart(
        topics_over_time=topics_over_time,
        selected_topic_label="Economy",
        normalize=True,
    )

    assert fig is not None
    assert len(fig.data) >= 1
    assert "Economy" in fig.layout.title.text


@pytest.mark.integration
def test_visualization_topic_distribution_bar_integration():
    valid_topic_info = pd.DataFrame({
        "CustomName": ["Economy", "Sports"],
        "Count": [15, 12],
    })

    fig = build_topic_distribution_bar(valid_topic_info, top_n=2)

    assert fig is not None
    assert len(fig.data) >= 1
    assert "المواضيع" in fig.layout.title.text
