import sys
import types
import pandas as pd
import pytest
from sklearn.feature_extraction.text import CountVectorizer

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

from core.topic_modeling import (
    build_vectorizer,
    build_topic_model,
    run_topic_modeling,
)


@pytest.mark.unit
def test_build_vectorizer_returns_count_vectorizer():
    vectorizer = build_vectorizer()

    assert isinstance(vectorizer, CountVectorizer)
    assert vectorizer.ngram_range == (1, 2)
    assert vectorizer.min_df == 2


@pytest.mark.unit
def test_build_vectorizer_merges_additional_stopwords():
    vectorizer = build_vectorizer(additional_stopwords=["customword", " AnotherWord "])

    stop_words = vectorizer.get_params()["stop_words"]
    assert "customword" in stop_words
    assert "anotherword" in stop_words


@pytest.mark.unit
def test_build_topic_model_uses_given_min_topic_size():
    topic_model = build_topic_model(min_topic_size=25)

    assert topic_model.min_topic_size == 25
    assert topic_model.language == "multilingual"
    assert topic_model.nr_topics == "auto"


class DummyTopicModel:
    def fit_transform(self, texts, embeddings):
        return [0, 1], [[0.9, 0.1], [0.2, 0.8]]


@pytest.mark.unit
def test_run_topic_modeling_adds_topic_column_and_returns_probs():
    df = pd.DataFrame({"clean_text": ["economy news", "sports match"]})
    texts = df["clean_text"].tolist()
    embeddings = [[0.1, 0.2], [0.3, 0.4]]

    analyzed_df, probs = run_topic_modeling(DummyTopicModel(), texts, embeddings, df)

    assert "topic" in analyzed_df.columns
    assert analyzed_df["topic"].tolist() == [0, 1]
    assert probs == [[0.9, 0.1], [0.2, 0.8]]
