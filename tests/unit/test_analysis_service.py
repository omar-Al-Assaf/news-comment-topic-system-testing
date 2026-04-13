import sys
import types
import pandas as pd
import pytest

# Fake bertopic module before importing project code
fake_bertopic = types.ModuleType("bertopic")

class FakeBERTopic:
    def __init__(self, *args, **kwargs):
        self.language = kwargs.get("language")
        self.vectorizer_model = kwargs.get("vectorizer_model")
        self.min_topic_size = kwargs.get("min_topic_size")
        self.nr_topics = kwargs.get("nr_topics")

fake_bertopic.BERTopic = FakeBERTopic
sys.modules.setdefault("bertopic", fake_bertopic)

# Fake sentence_transformers module before importing project code
fake_st = types.ModuleType("sentence_transformers")

class FakeSentenceTransformer:
    def __init__(self, *args, **kwargs):
        self.model_name = args[0] if args else None

    def encode(self, texts, show_progress_bar=False):
        return [[0.0] for _ in texts]

fake_st.SentenceTransformer = FakeSentenceTransformer
sys.modules.setdefault("sentence_transformers", fake_st)

from core.analysis_service import run_full_analysis


@pytest.mark.unit
def test_run_full_analysis_raises_when_validation_fails(mocker):
    mocker.patch("core.analysis_service.load_dataset", return_value=pd.DataFrame())
    mocker.patch(
        "core.analysis_service.validate_dataset",
        return_value=(False, "invalid dataset")
    )

    with pytest.raises(ValueError, match="invalid dataset"):
        run_full_analysis(
            file_source="dummy.csv",
            sample_size=10,
            min_comments_per_post=2,
            min_topic_size=5,
            nr_bins=2,
            text_col="text",
            date_col="date",
            post_col="post_id",
        )


@pytest.mark.unit
def test_run_full_analysis_raises_when_clean_df_is_empty(mocker):
    raw_df = pd.DataFrame({"text": ["a"], "date": ["2024-01-01"], "post_id": [1]})
    base_df = pd.DataFrame({"text": ["a"], "date": ["2024-01-01"], "post_id": [1]})

    mocker.patch("core.analysis_service.load_dataset", return_value=raw_df)
    mocker.patch("core.analysis_service.validate_dataset", return_value=(True, "ok"))
    mocker.patch("core.analysis_service.summarize_dataset", return_value={"rows": 1})
    mocker.patch("core.analysis_service.filter_active_posts", return_value=raw_df)
    mocker.patch("core.analysis_service.prepare_base_dataframe", return_value=base_df)
    mocker.patch("core.analysis_service.sample_records", return_value=base_df)
    mocker.patch("core.analysis_service.preprocess_comments", return_value=pd.DataFrame())

    with pytest.raises(ValueError, match="لا توجد بيانات كافية بعد التنظيف"):
        run_full_analysis(
            file_source="dummy.csv",
            sample_size=10,
            min_comments_per_post=2,
            min_topic_size=5,
            nr_bins=2,
            text_col="text",
            date_col="date",
            post_col="post_id",
        )


@pytest.mark.unit
def test_run_full_analysis_returns_expected_keys_on_success(mocker):
    raw_df = pd.DataFrame({
        "text": ["economy comment", "sports comment"],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "post_id": [1, 1],
    })

    sampled_df = raw_df.copy()

    clean_df = pd.DataFrame({
        "clean_text": ["economy inflation", "sports team"],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "post_id": [1, 1],
        "topic": [0, 1],
    })

    topic_info = pd.DataFrame({
        "Topic": [0, 1, -1],
        "Count": [10, 8, 2],
    })

    topic_info_display = pd.DataFrame({
        "Topic": [0, 1],
        "CustomName": ["Economy", "Sports"],
    })

    df_valid = pd.DataFrame({
        "clean_text": ["economy inflation", "sports team"],
        "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "post_id": [1, 1],
        "topic": [0, 1],
        "month": ["2024-01", "2024-01"],
    })

    topics_over_time = pd.DataFrame({
        "Timestamp": ["2024-01", "2024-01"],
        "Topic": [0, 1],
        "Frequency": [5, 4],
    })

    class DummyTopicModel:
        def get_topic_info(self):
            return topic_info

    mocker.patch("core.analysis_service.load_dataset", return_value=raw_df)
    mocker.patch("core.analysis_service.validate_dataset", return_value=(True, "ok"))
    mocker.patch("core.analysis_service.summarize_dataset", return_value={"rows": 2})
    mocker.patch("core.analysis_service.filter_active_posts", return_value=raw_df)
    mocker.patch("core.analysis_service.prepare_base_dataframe", return_value=raw_df)
    mocker.patch("core.analysis_service.sample_records", return_value=sampled_df)
    mocker.patch("core.analysis_service.preprocess_comments", return_value=clean_df)
    mocker.patch("core.analysis_service.build_embedder", return_value="dummy_embedder")
    mocker.patch("core.analysis_service.generate_embeddings", return_value=[[0.1], [0.2]])
    mocker.patch("core.analysis_service.build_topic_model", return_value=DummyTopicModel())
    mocker.patch(
        "core.analysis_service.run_topic_modeling",
        return_value=(clean_df, [[0.8], [0.7]])
    )
    mocker.patch("core.analysis_service.prepare_topic_display", return_value=topic_info_display)
    mocker.patch("core.analysis_service.build_valid_topics_df", return_value=df_valid)
    mocker.patch("core.analysis_service.add_month_column", return_value=df_valid)
    mocker.patch("core.analysis_service.analyze_topics_over_time", return_value=topics_over_time)
    mocker.patch(
        "core.analysis_service.attach_time_labels",
        return_value=topics_over_time.assign(topic_label=["Economy", "Sports"])
    )

    result = run_full_analysis(
        file_source="dummy.csv",
        sample_size=10,
        min_comments_per_post=2,
        min_topic_size=5,
        nr_bins=2,
        text_col="text",
        date_col="date",
        post_col="post_id",
    )

    expected_keys = {
        "summary",
        "raw_df",
        "filtered_df",
        "sampled_df",
        "clean_df",
        "topic_info_display",
        "df_valid",
        "topics_over_time",
    }

    assert set(result.keys()) == expected_keys
    assert result["summary"] == {"rows": 2}
    assert not result["clean_df"].empty


@pytest.mark.unit
def test_run_full_analysis_raises_when_no_valid_topics_after_analysis(mocker):
    raw_df = pd.DataFrame({
        "text": ["economy comment"],
        "date": pd.to_datetime(["2024-01-01"]),
        "post_id": [1],
    })

    clean_df = pd.DataFrame({
        "clean_text": ["economy inflation"],
        "date": pd.to_datetime(["2024-01-01"]),
        "post_id": [1],
        "topic": [0],
    })

    topic_info = pd.DataFrame({"Topic": [0], "Count": [5]})
    topic_info_display = pd.DataFrame({"Topic": [0], "CustomName": ["Economy"]})

    class DummyTopicModel:
        def get_topic_info(self):
            return topic_info

    mocker.patch("core.analysis_service.load_dataset", return_value=raw_df)
    mocker.patch("core.analysis_service.validate_dataset", return_value=(True, "ok"))
    mocker.patch("core.analysis_service.summarize_dataset", return_value={"rows": 1})
    mocker.patch("core.analysis_service.filter_active_posts", return_value=raw_df)
    mocker.patch("core.analysis_service.prepare_base_dataframe", return_value=raw_df)
    mocker.patch("core.analysis_service.sample_records", return_value=raw_df)
    mocker.patch("core.analysis_service.preprocess_comments", return_value=clean_df)
    mocker.patch("core.analysis_service.build_embedder", return_value="dummy_embedder")
    mocker.patch("core.analysis_service.generate_embeddings", return_value=[[0.1]])
    mocker.patch("core.analysis_service.build_topic_model", return_value=DummyTopicModel())
    mocker.patch("core.analysis_service.run_topic_modeling", return_value=(clean_df, [[0.9]]))
    mocker.patch("core.analysis_service.prepare_topic_display", return_value=topic_info_display)
    mocker.patch("core.analysis_service.build_valid_topics_df", return_value=pd.DataFrame())
    mocker.patch("core.analysis_service.add_month_column", return_value=pd.DataFrame())

    with pytest.raises(ValueError, match="لا توجد مواضيع صالحة بعد التحليل"):
        run_full_analysis(
            file_source="dummy.csv",
            sample_size=10,
            min_comments_per_post=2,
            min_topic_size=5,
            nr_bins=2,
            text_col="text",
            date_col="date",
            post_col="post_id",
        )
