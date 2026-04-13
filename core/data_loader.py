import pandas as pd

DEFAULT_TEXT_COL = "message"
DEFAULT_DATE_COL = "created_time"
DEFAULT_POST_COL = "post_name"


def load_dataset(file_obj):
    return pd.read_csv(file_obj)


def validate_dataset(
    df,
    text_col=DEFAULT_TEXT_COL,
    date_col=DEFAULT_DATE_COL,
    post_col=DEFAULT_POST_COL
):
    required_columns = [text_col, date_col, post_col]
    missing = [c for c in required_columns if c not in df.columns]

    if missing:
        return False, f"الأعمدة الناقصة: {missing}"

    if df.empty:
        return False, "الملف فارغ."

    return True, ""


def add_true_post_id(df, post_col=DEFAULT_POST_COL):
    data = df.copy()
    data["post_id_true"] = data[post_col].astype(str).str.split("_", n=1).str[1]
    return data


def summarize_dataset(df, post_col=DEFAULT_POST_COL):
    data = add_true_post_id(df, post_col=post_col)

    num_comments = len(data)
    num_posts = data["post_id_true"].nunique(dropna=True)
    comments_per_post = data.groupby("post_id_true").size()
    avg_comments_per_post = comments_per_post.mean()

    return {
        "num_comments": num_comments,
        "num_posts": num_posts,
        "avg_comments_per_post": avg_comments_per_post
    }


def filter_active_posts(df, min_comments_per_post=3, post_col=DEFAULT_POST_COL):
    data = add_true_post_id(df, post_col=post_col)

    comments_per_post = data.groupby("post_id_true").size()
    active_posts = comments_per_post[comments_per_post > min_comments_per_post].index

    filtered_df = data[data["post_id_true"].isin(active_posts)].copy()
    return filtered_df


def sample_records(df, sample_size=10000, random_state=42):
    data = df.copy()

    if sample_size is None or sample_size >= len(data):
        return data

    return data.sample(n=sample_size, random_state=random_state).copy()


def prepare_base_dataframe(
    df,
    text_col=DEFAULT_TEXT_COL,
    date_col=DEFAULT_DATE_COL,
    post_col=DEFAULT_POST_COL,
    user_id_col="from_id",
    user_name_col="from_name"
):
    data = df.copy()

    if "post_id_true" not in data.columns:
        data["post_id_true"] = data[post_col].astype(str).str.split("_", n=1).str[1]

    rename_map = {
        text_col: "text",
        date_col: "date"
    }

    if user_id_col in data.columns:
        rename_map[user_id_col] = "user_id"

    if user_name_col in data.columns:
        rename_map[user_name_col] = "user_name"

    if post_col in data.columns:
        rename_map[post_col] = "raw_post_name"

    data = data.rename(columns=rename_map)

    data = data.dropna(subset=["text", "date", "post_id_true"])
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data = data.dropna(subset=["date"]).copy()

    return data
