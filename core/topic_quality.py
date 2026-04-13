import pandas as pd


def _ensure_list(value):
    if isinstance(value, list):
        return [x for x in value if str(x).strip()]
    if pd.isna(value):
        return []
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return []
        return [value]
    return [value]


def _word_count(text):
    return len(str(text).split())


def _confidence_label(score, topic_id):
    if topic_id == -1:
        return "ضوضاء", "noise"
    if score >= 80:
        return "مرتفعة", "high"
    if score >= 60:
        return "متوسطة", "medium"
    return "منخفضة", "low"


def _confidence_reason(score, profile, keyword_count, rep_doc_count):
    if profile == "noise":
        return "هذا الصف يمثل تعليقات لم تتجمع في موضوع متماسك بما يكفي، لذلك لا تُعامل كموضوع واضح."

    if score >= 80:
        return (
            "الثقة مرتفعة لأن الموضوع يملك حجمًا جيدًا، وكلمات مفتاحية واضحة، "
            "وتعليقات ممثلة تساعد على تفسيره بشكل متماسك."
        )

    if score >= 60:
        return (
            "الثقة متوسطة لأن الموضوع قابل للفهم، لكنه ليس شديد التخصص أو أن إشاراته الدلالية ما تزال محدودة نسبيًا."
        )

    if profile == "general":
        return (
            "الثقة منخفضة لأن الموضوع عام أو مختلط، ولم تظهر له إشارات تخصصية كافية لبناء تسمية أكثر دقة."
        )

    if keyword_count <= 2 or rep_doc_count == 0:
        return (
            "الثقة منخفضة لأن الكلمات المفتاحية أو التعليقات الممثلة غير كافية لتأكيد موضوع محدد بدرجة عالية."
        )

    return "الثقة منخفضة لأن هذا الموضوع ما يزال بحاجة إلى إشارات أوضح حتى يصبح أكثر موثوقية."


def add_topic_confidence(topic_info_display: pd.DataFrame) -> pd.DataFrame:
    data = topic_info_display.copy()

    if data.empty:
        data["ConfidenceScore"] = []
        data["ConfidenceLabel"] = []
        data["ConfidenceClass"] = []
        data["ConfidenceReason"] = []
        return data

    valid = data[data["Topic"] != -1].copy()
    median_count = float(valid["Count"].median()) if not valid.empty else 1.0
    median_count = max(median_count, 1.0)

    confidence_scores = []
    confidence_labels = []
    confidence_classes = []
    confidence_reasons = []

    for _, row in data.iterrows():
        topic_id = int(row.get("Topic", -1))
        profile = str(row.get("DetectedProfile", "general") or "general")
        count = int(row.get("Count", 0) or 0)

        clean_keywords = _ensure_list(row.get("CleanKeywords", []))
        rep_docs = _ensure_list(row.get("Representative_Docs", []))

        keyword_count = len(clean_keywords)
        rep_doc_count = len(rep_docs)

        avg_doc_len = 0.0
        if rep_docs:
            avg_doc_len = sum(_word_count(x) for x in rep_docs) / len(rep_docs)

        if topic_id == -1:
            score = 0
        else:
            count_norm = min(count / median_count, 2.0) / 2.0
            count_points = count_norm * 35

            if profile == "general":
                profile_points = 10
            else:
                profile_points = 25

            keyword_points = min(keyword_count, 5) / 5 * 20

            doc_count_points = min(rep_doc_count, 3) / 3 * 10
            doc_quality_points = min(avg_doc_len, 18) / 18 * 10
            doc_points = doc_count_points + doc_quality_points

            score = round(count_points + profile_points + keyword_points + doc_points)

            if profile == "general":
                score = min(score, 72)
            if keyword_count <= 1:
                score = min(score, 58)
            if rep_doc_count == 0:
                score = min(score, 60)

            score = max(0, min(100, score))

        label, label_class = _confidence_label(score, topic_id)
        reason = _confidence_reason(score, profile, keyword_count, rep_doc_count)

        confidence_scores.append(score)
        confidence_labels.append(label)
        confidence_classes.append(label_class)
        confidence_reasons.append(reason)

    data["ConfidenceScore"] = confidence_scores
    data["ConfidenceLabel"] = confidence_labels
    data["ConfidenceClass"] = confidence_classes
    data["ConfidenceReason"] = confidence_reasons
    return data
