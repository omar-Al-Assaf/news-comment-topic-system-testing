def build_valid_topics_df(df, valid_topics):
    return df[df["topic"].isin(valid_topics)].copy()

def add_month_column(df):
    data = df.copy()
    data["month"] = data["date"].dt.to_period("M").astype(str)
    return data

def analyze_topics_over_time(topic_model, df, nr_bins=2):
    return topic_model.topics_over_time(
        df["clean_text"].tolist(),
        df["month"].tolist(),
        df["topic"].tolist(),
        nr_bins=nr_bins
    )

def attach_time_labels(topics_over_time, topic_info_labeled):
    topic_name_map = dict(zip(topic_info_labeled["Topic"], topic_info_labeled["CustomName"]))
    data = topics_over_time.copy()
    data["topic_label"] = data["Topic"].map(topic_name_map)
    return data
