from core.data_loader import (
    load_dataset,
    validate_dataset,
    summarize_dataset,
    filter_active_posts,
    sample_records,
    prepare_base_dataframe
)
from core.preprocessing import preprocess_comments
from core.embedding_service import build_embedder, generate_embeddings
from core.topic_modeling import build_topic_model, run_topic_modeling
from core.trend_analysis import (
    build_valid_topics_df,
    add_month_column,
    analyze_topics_over_time,
    attach_time_labels
)
from core.topic_naming import prepare_topic_display


def run_full_analysis(
    file_source,
    sample_size,
    min_comments_per_post,
    min_topic_size,
    nr_bins,
    text_col,
    date_col,
    post_col,
    additional_stopwords=None
):
    df = load_dataset(file_source)

    ok, msg = validate_dataset(
        df,
        text_col=text_col,
        date_col=date_col,
        post_col=post_col
    )
    if not ok:
        raise ValueError(msg)

    summary = summarize_dataset(df, post_col=post_col)

    filtered_df = filter_active_posts(
        df,
        min_comments_per_post=min_comments_per_post,
        post_col=post_col
    )

    base_df = prepare_base_dataframe(
        filtered_df,
        text_col=text_col,
        date_col=date_col,
        post_col=post_col
    )

    sampled_df = sample_records(base_df, sample_size=sample_size, random_state=42)
    df2 = preprocess_comments(sampled_df)

    if df2.empty:
        raise ValueError("لا توجد بيانات كافية بعد التنظيف.")

    texts = df2["clean_text"].tolist()

    embedder = build_embedder()
    embeddings = generate_embeddings(embedder, texts)

    topic_model = build_topic_model(
        min_topic_size=min_topic_size,
        additional_stopwords=additional_stopwords
    )

    df2, probs = run_topic_modeling(topic_model, texts, embeddings, df2)

    topic_info = topic_model.get_topic_info().copy()
    topic_info_display = prepare_topic_display(topic_info)

    valid_topics = [t for t in topic_info_display["Topic"].tolist() if t != -1]

    df_valid = build_valid_topics_df(df2, valid_topics)
    df_valid = add_month_column(df_valid)

    if df_valid.empty:
        raise ValueError("لا توجد مواضيع صالحة بعد التحليل.")

    topic_name_map = dict(zip(topic_info_display["Topic"], topic_info_display["CustomName"]))
    df_valid["topic_label"] = df_valid["topic"].map(topic_name_map)

    topics_over_time = analyze_topics_over_time(topic_model, df_valid, nr_bins=nr_bins)
    topics_over_time = attach_time_labels(topics_over_time, topic_info_display)

    return {
        "summary": summary,
        "raw_df": df,
        "filtered_df": filtered_df,
        "sampled_df": sampled_df,
        "clean_df": df2,
        "topic_info_display": topic_info_display,
        "df_valid": df_valid,
        "topics_over_time": topics_over_time
    }
