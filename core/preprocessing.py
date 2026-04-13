import re
import html
import pandas as pd


# كلمات حوارية/ضعيفة إذا سيطرت على التعليق يصبح غير مفيد موضوعيًا
WEAK_TEXT_WORDS = {
    "just", "like", "really", "yeah", "yes", "okay", "ok", "lol", "haha",
    "dont", "didnt", "know", "think", "thing", "things", "stuff",
    "going", "go", "get", "got", "one", "well", "thank", "thanks",
    "man", "people", "person", "persons"
}

# كلمات قصيرة نسمح بها لأنها قد تكون مهمة موضوعيًا
ALLOWED_SHORT_TOKENS = {
    "us", "uk", "eu"
}

CONTRACTION_PATTERNS = [
    (r"\bwon't\b", "will not"),
    (r"\bcan't\b", "can not"),
    (r"\bshan't\b", "shall not"),
    (r"\bain't\b", "is not"),
    (r"\bi'm\b", "i am"),
    (r"\bi've\b", "i have"),
    (r"\bi'll\b", "i will"),
    (r"\bi'd\b", "i would"),
    (r"\byou're\b", "you are"),
    (r"\byou've\b", "you have"),
    (r"\byou'll\b", "you will"),
    (r"\bwe're\b", "we are"),
    (r"\bwe've\b", "we have"),
    (r"\bwe'll\b", "we will"),
    (r"\bthey're\b", "they are"),
    (r"\bthey've\b", "they have"),
    (r"\bthey'll\b", "they will"),
    (r"\bhe's\b", "he is"),
    (r"\bshe's\b", "she is"),
    (r"\bit's\b", "it is"),
    (r"\bthat's\b", "that is"),
    (r"\bthere's\b", "there is"),
    (r"\bwhat's\b", "what is"),
    (r"\blet's\b", "let us"),
    (r"n't\b", " not"),
    (r"'re\b", " are"),
    (r"'ve\b", " have"),
    (r"'ll\b", " will"),
    (r"'d\b", " would"),
    (r"'m\b", " am"),
]


def expand_contractions(text: str) -> str:
    for pattern, replacement in CONTRACTION_PATTERNS:
        text = re.sub(pattern, replacement, text)
    return text


def normalize_text(text) -> str:
    if pd.isna(text):
        return ""

    text = html.unescape(str(text))
    text = text.lower()

    # إزالة الروابط والـ mentions والـ hashtags
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"#\w+", " ", text)

    # توسيع الاختصارات
    text = expand_contractions(text)

    # تقليل تكرار الحروف: cooooool -> cool
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)

    # حذف أي شيء ليس حرفًا أو فراغًا
    text = re.sub(r"[^a-z\s]", " ", text)

    # توحيد الفراغات
    text = re.sub(r"\s+", " ", text).strip()

    return text


def tokenize_clean_text(cleaned_text: str):
    tokens = []

    for token in cleaned_text.split():
        if len(token) >= 3 or token in ALLOWED_SHORT_TOKENS:
            tokens.append(token)

    return tokens


def is_informative(tokens, min_meaningful_tokens=3):
    if not tokens:
        return False

    if len(tokens) < min_meaningful_tokens:
        return False

    non_weak_count = sum(1 for t in tokens if t not in WEAK_TEXT_WORDS)

    if non_weak_count < 2:
        return False

    # إذا كل التوكنز تقريبًا ضعيفة، فالنص غير مفيد موضوعيًا
    if non_weak_count == 0:
        return False

    # فلترة نصوص شديدة التكرار مثل: yes yes yes yes
    unique_ratio = len(set(tokens)) / max(len(tokens), 1)
    if len(tokens) >= 4 and unique_ratio < 0.4:
        return False

    return True


def preprocess_comments(
    df,
    text_col="text",
    min_meaningful_tokens=3,
    drop_duplicates=True
):
    data = df.copy()

    if text_col not in data.columns:
        raise ValueError(f"العمود '{text_col}' غير موجود في البيانات.")

    data = data.dropna(subset=[text_col]).copy()

    data["normalized_text"] = data[text_col].apply(normalize_text)
    data["clean_tokens"] = data["normalized_text"].apply(tokenize_clean_text)
    data["clean_token_count"] = data["clean_tokens"].apply(len)
    data["informative_token_count"] = data["clean_tokens"].apply(
        lambda toks: sum(1 for t in toks if t not in WEAK_TEXT_WORDS)
    )

    data = data[
        data["clean_tokens"].apply(
            lambda toks: is_informative(toks, min_meaningful_tokens=min_meaningful_tokens)
        )
    ].copy()

    data["clean_text"] = data["clean_tokens"].apply(lambda toks: " ".join(toks))
    data = data[data["clean_text"].str.strip() != ""].copy()

    if drop_duplicates:
        data = data.drop_duplicates(subset=["clean_text"]).copy()

    return data
