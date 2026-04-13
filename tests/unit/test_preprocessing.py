import pandas as pd
import pytest

from core.preprocessing import (
    expand_contractions,
    normalize_text,
    tokenize_clean_text,
    is_informative,
    preprocess_comments,
)


@pytest.mark.unit
def test_expand_contractions_expands_common_forms():
    text = "I'm sure we won't say it's done"
    result = expand_contractions(text.lower())

    assert "i am" in result
    assert "will not" in result
    assert "it is" in result


@pytest.mark.unit
def test_normalize_text_removes_urls_mentions_hashtags_and_lowercases():
    text = "Visit HTTP://example.com NOW @User #Breaking"
    result = normalize_text(text)

    assert "http" not in result
    assert "example" not in result
    assert "user" not in result
    assert "breaking" not in result
    assert result == result.lower()


@pytest.mark.unit
def test_normalize_text_returns_empty_string_for_nan():
    result = normalize_text(float("nan"))
    assert result == ""


@pytest.mark.unit
def test_tokenize_clean_text_keeps_allowed_short_tokens_and_long_words():
    text = "us uk eu ai economy news"
    result = tokenize_clean_text(text)

    assert "us" in result
    assert "uk" in result
    assert "eu" in result
    assert "economy" in result
    assert "news" in result
    assert "ai" not in result


@pytest.mark.unit
def test_is_informative_returns_false_for_empty_tokens():
    assert is_informative([]) is False


@pytest.mark.unit
def test_is_informative_returns_false_for_weak_repetitive_tokens():
    tokens = ["yes", "yes", "yes", "yes"]
    assert is_informative(tokens) is False


@pytest.mark.unit
def test_is_informative_returns_true_for_meaningful_tokens():
    tokens = ["economy", "market", "inflation"]
    assert is_informative(tokens) is True


@pytest.mark.unit
def test_preprocess_comments_raises_when_text_column_missing():
    df = pd.DataFrame({"wrong_col": ["hello world"]})

    with pytest.raises(ValueError, match="غير موجود"):
        preprocess_comments(df, text_col="text")


@pytest.mark.unit
def test_preprocess_comments_creates_expected_columns_and_filters_rows():
    df = pd.DataFrame(
        {
            "text": [
                "The economy is getting worse because of inflation",
                "yes yes yes yes",
                None,
                "Visit https://example.com for market updates",
            ]
        }
    )

    result = preprocess_comments(df, text_col="text")

    assert "normalized_text" in result.columns
    assert "clean_tokens" in result.columns
    assert "clean_token_count" in result.columns
    assert "informative_token_count" in result.columns
    assert "clean_text" in result.columns
    assert not result.empty


@pytest.mark.unit
def test_preprocess_comments_removes_duplicate_clean_text_when_enabled():
    df = pd.DataFrame(
        {
            "text": [
                "The economy is growing fast",
                "the economy is growing fast!!!",
            ]
        }
    )

    result = preprocess_comments(df, text_col="text", drop_duplicates=True)
    assert len(result) == 1
