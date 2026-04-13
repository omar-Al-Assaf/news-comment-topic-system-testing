from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction import text as sklearn_text


BASE_EXTRA_STOPWORDS = [
    "just", "like", "im", "ive", "dont", "didnt", "thats",
    "yes", "really", "know", "going", "got", "get",
    "one", "want", "well", "would", "could", "also",
    "still", "much", "many", "even", "say", "said",
    "make", "made", "let", "lets"
]


def build_vectorizer(additional_stopwords=None):
    custom_stopwords = list(sklearn_text.ENGLISH_STOP_WORDS)
    custom_stopwords += BASE_EXTRA_STOPWORDS

    if additional_stopwords:
        custom_stopwords += [
            str(x).strip().lower()
            for x in additional_stopwords
            if str(x).strip()
        ]

    custom_stopwords = list(set(custom_stopwords))

    return CountVectorizer(
        stop_words=custom_stopwords,
        ngram_range=(1, 2),
        min_df=2
    )


def build_topic_model(min_topic_size=80, additional_stopwords=None):
    return BERTopic(
        language="multilingual",
        vectorizer_model=build_vectorizer(additional_stopwords=additional_stopwords),
        min_topic_size=min_topic_size,
        nr_topics="auto"
    )


def run_topic_modeling(topic_model, texts, embeddings, df):
    topics, probs = topic_model.fit_transform(texts, embeddings)
    analyzed_df = df.copy()
    analyzed_df["topic"] = topics
    return analyzed_df, probs
