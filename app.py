import os
import pandas as pd
import streamlit as st

from core.data_loader import (
    load_dataset,
    DEFAULT_TEXT_COL,
    DEFAULT_DATE_COL,
    DEFAULT_POST_COL,
)
from core.analysis_service import run_full_analysis
from core.chart_panel import render_chart_panel
from core.topic_quality import add_topic_confidence


DEFAULT_CSV_PATH = "/content/drive/MyDrive/semester project/news_comment_topic_system/fb_news_comments_1000K_hashed.csv"

PROFILE_AR = {
    "general": "عام",
    "politics_news": "سياسة وأخبار",
    "public_safety": "أمن عام",
    "health_medical": "صحة",
    "business_finance": "اقتصاد وأعمال",
    "technology": "تقنية",
    "customer_feedback": "خدمة العملاء",
    "sports": "رياضة",
    "education": "تعليم",
    "society_culture": "مجتمع وثقافة",
    "media_entertainment": "إعلام وترفيه",
    "noise": "ضوضاء"
}

st.set_page_config(
    page_title="News Comment Topic Analysis System",
    layout="wide",
)

st.markdown(
    """
<style>
.block-container {
    padding-top: 1.1rem;
    padding-bottom: 2rem;
    max-width: 1500px;
}
.main-title {
    font-size: 2.9rem;
    font-weight: 800;
    margin-bottom: 0.2rem;
}
.glass-card {
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 22px;
    padding: 20px;
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.18);
}
.hero-card {
    margin-top: 14px;
    margin-bottom: 18px;
    padding: 24px;
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.035));
    border: 1px solid rgba(255,255,255,0.10);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    box-shadow: 0 16px 44px rgba(0,0,0,0.22);
}
.hero-label {
    font-size: 14px;
    opacity: 0.82;
    margin-bottom: 8px;
}
.hero-title {
    font-size: 2.5rem;
    font-weight: 800;
    line-height: 1.22;
    word-break: break-word;
    white-space: normal;
    margin-bottom: 16px;
}
.hero-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(140px, 1fr));
    gap: 12px;
}
.hero-mini {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 14px 16px;
}
.hero-mini-label {
    font-size: 13px;
    opacity: 0.78;
    margin-bottom: 6px;
}
.hero-mini-value {
    font-size: 1.1rem;
    font-weight: 700;
    line-height: 1.25;
    word-break: break-word;
}
.small-muted {
    opacity: 0.82;
    font-size: 14px;
}
.topic-badge {
    display: inline-block;
    padding: 6px 10px;
    border-radius: 999px;
    background: rgba(90,169,255,0.16);
    border: 1px solid rgba(90,169,255,0.24);
    font-size: 13px;
    margin-top: 10px;
}
.summary-list {
    margin: 0;
    padding-right: 18px;
    line-height: 1.9;
}
.conf-grid {
    display: grid;
    grid-template-columns: 150px 1fr;
    gap: 18px;
    align-items: center;
}
.conf-score-wrap {
    text-align: center;
    padding: 14px;
    border-radius: 18px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
}
.conf-score {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1;
}
.conf-pill {
    display: inline-block;
    padding: 6px 12px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
    margin-top: 10px;
}
.conf-high {
    background: rgba(34,197,94,0.18);
    border: 1px solid rgba(34,197,94,0.28);
}
.conf-medium {
    background: rgba(245,158,11,0.18);
    border: 1px solid rgba(245,158,11,0.28);
}
.conf-low {
    background: rgba(239,68,68,0.18);
    border: 1px solid rgba(239,68,68,0.28);
}
.conf-noise {
    background: rgba(148,163,184,0.18);
    border: 1px solid rgba(148,163,184,0.28);
}
.conf-track {
    width: 100%;
    height: 12px;
    border-radius: 999px;
    background: rgba(255,255,255,0.08);
    overflow: hidden;
    margin: 10px 0 12px;
}
.conf-fill {
    height: 100%;
    border-radius: 999px;
}
.fill-high {
    background: linear-gradient(90deg, #16a34a, #4ade80);
}
.fill-medium {
    background: linear-gradient(90deg, #d97706, #fbbf24);
}
.fill-low {
    background: linear-gradient(90deg, #dc2626, #fb7185);
}
.fill-noise {
    background: linear-gradient(90deg, #64748b, #94a3b8);
}
</style>
""",
    unsafe_allow_html=True,
)


def safe_text(value, fallback="غير متاح"):
    if pd.isna(value):
        return fallback
    text = str(value).strip()
    return text if text else fallback


def profile_ar(profile_code):
    return PROFILE_AR.get(str(profile_code), str(profile_code))


def confidence_css_class(conf_class: str):
    mapping = {
        "high": "conf-high",
        "medium": "conf-medium",
        "low": "conf-low",
        "noise": "conf-noise",
    }
    return mapping.get(conf_class, "conf-low")


def confidence_fill_class(conf_class: str):
    mapping = {
        "high": "fill-high",
        "medium": "fill-medium",
        "low": "fill-low",
        "noise": "fill-noise",
    }
    return mapping.get(conf_class, "fill-low")


def render_confidence_card(row, title="درجة الثقة في الموضوع"):
    score = int(row.get("ConfidenceScore", 0))
    label = safe_text(row.get("ConfidenceLabel", "غير معروفة"))
    conf_class = safe_text(row.get("ConfidenceClass", "low"))
    reason = safe_text(row.get("ConfidenceReason", "لا يوجد تفسير متاح."))
    css_class = confidence_css_class(conf_class)
    fill_class = confidence_fill_class(conf_class)

    st.markdown(
        f"""
        <div class="glass-card">
            <div class="small-muted">{title}</div>
            <div class="conf-grid">
                <div class="conf-score-wrap">
                    <div class="conf-score">{score}/100</div>
                    <div class="conf-pill {css_class}">{label}</div>
                </div>
                <div>
                    <div class="conf-track">
                        <div class="conf-fill {fill_class}" style="width:{score}%;"></div>
                    </div>
                    <div style="font-size:15px; line-height:1.75; opacity:0.92;">{reason}</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.markdown('<div class="main-title">News Comment Topic Analysis System</div>', unsafe_allow_html=True)

st.sidebar.header("الإعدادات")

use_default_file = st.sidebar.checkbox("استخدم ملف المشروع الموجود في Drive", value=True)

uploaded_file = None
if not use_default_file:
    uploaded_file = st.sidebar.file_uploader("رفع ملف CSV", type=["csv"])

sample_size = st.sidebar.number_input(
    "حجم عينة التعليقات للتحليل",
    min_value=1000,
    value=3000,
    step=1000,
)

min_comments_per_post = st.sidebar.number_input(
    "الحد الأدنى لتعليقات المنشور",
    min_value=1,
    value=3,
    step=1,
)

min_topic_size = st.sidebar.number_input(
    "الحد الأدنى لحجم الموضوع",
    min_value=5,
    value=80,
    step=5,
)

nr_bins = st.sidebar.number_input(
    "عدد الحاويات الزمنية",
    min_value=1,
    value=2,
    step=1,
)

top_n_charts = st.sidebar.number_input(
    "عدد المواضيع في الرسوم",
    min_value=3,
    value=8,
    step=1,
)

if use_default_file:
    if os.path.exists(DEFAULT_CSV_PATH):
        file_source = DEFAULT_CSV_PATH
        st.sidebar.success("سيتم استخدام ملف CSV الموجود داخل مجلد المشروع.")
    else:
        file_source = None
        st.sidebar.error("ملف المشروع غير موجود في المسار المتوقع.")
else:
    if uploaded_file is None:
        file_source = None
        st.sidebar.info("ارفع ملف CSV من الشريط الجانبي أو فعّل خيار استخدام ملف المشروع.")
    else:
        file_source = uploaded_file
        st.sidebar.success("تم استلام الملف المرفوع.")

columns = []
if file_source is not None:
    try:
        preview_df = load_dataset(file_source)
        columns = preview_df.columns.tolist()
    except Exception:
        columns = []

default_text_index = columns.index(DEFAULT_TEXT_COL) if DEFAULT_TEXT_COL in columns else 0
default_date_index = columns.index(DEFAULT_DATE_COL) if DEFAULT_DATE_COL in columns else 0
default_post_index = columns.index(DEFAULT_POST_COL) if DEFAULT_POST_COL in columns else 0

text_col = st.sidebar.selectbox(
    "عمود النص",
    options=columns if columns else [DEFAULT_TEXT_COL],
    index=default_text_index if columns else 0,
)

date_col = st.sidebar.selectbox(
    "عمود التاريخ",
    options=columns if columns else [DEFAULT_DATE_COL],
    index=default_date_index if columns else 0,
)

post_col = st.sidebar.selectbox(
    "عمود معرف المنشور المركب",
    options=columns if columns else [DEFAULT_POST_COL],
    index=default_post_index if columns else 0,
)

run_btn = st.sidebar.button("تشغيل التحليل", use_container_width=True)

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

if run_btn:
    if file_source is None:
        st.error("لا يوجد ملف لإجراء التحليل عليه.")
        st.stop()

    with st.spinner("جاري تنفيذ التحليل..."):
        try:
            results = run_full_analysis(
                file_source=file_source,
                sample_size=sample_size,
                min_comments_per_post=min_comments_per_post,
                min_topic_size=min_topic_size,
                nr_bins=nr_bins,
                text_col=text_col,
                date_col=date_col,
                post_col=post_col,
                additional_stopwords=[],
            )
            st.session_state.analysis_results = results
        except Exception as e:
            st.error(f"حدث خطأ أثناء تنفيذ التحليل: {e}")
            st.stop()

results = st.session_state.analysis_results

if results is None:
    st.info("اختر الإعدادات المناسبة من الشريط الجانبي ثم اضغط تشغيل التحليل.")
    st.stop()

summary = results["summary"]
sampled_df = results["sampled_df"]
df2 = results["clean_df"]
topic_info_display = add_topic_confidence(results["topic_info_display"])
df_valid = results["df_valid"]
topics_over_time = results["topics_over_time"]

topic_info_display["ArabicProfile"] = topic_info_display["DetectedProfile"].apply(profile_ar) if "DetectedProfile" in topic_info_display.columns else "عام"

valid_topic_info = topic_info_display[topic_info_display["Topic"] != -1].copy()
valid_topic_info = valid_topic_info.sort_values(
    ["Count", "ConfidenceScore"],
    ascending=[False, False]
).reset_index(drop=True)

if valid_topic_info.empty:
    st.warning("لم يتم اكتشاف مواضيع صالحة بهذه الإعدادات. جرّب رفع حجم العينة أو خفض الحد الأدنى لحجم الموضوع.")
    st.stop()

if "CleanKeywords" not in valid_topic_info.columns:
    valid_topic_info["CleanKeywords"] = [[] for _ in range(len(valid_topic_info))]

valid_topic_info["ArabicProfile"] = valid_topic_info["DetectedProfile"].apply(profile_ar) if "DetectedProfile" in valid_topic_info.columns else "عام"
valid_topic_info["UI_Label"] = valid_topic_info.apply(
    lambda r: f"{safe_text(r['CustomName'])} [#{int(r['Topic'])}]",
    axis=1,
)

noise_count = 0
if not topic_info_display[topic_info_display["Topic"] == -1].empty:
    noise_count = int(topic_info_display[topic_info_display["Topic"] == -1]["Count"].iloc[0])

clean_count = len(df2)
noise_ratio = (noise_count / clean_count * 100) if clean_count > 0 else 0.0
num_topics = len(valid_topic_info)
avg_confidence = float(valid_topic_info["ConfidenceScore"].mean()) if not valid_topic_info.empty else 0.0
high_conf_topics = int((valid_topic_info["ConfidenceLabel"] == "مرتفعة").sum())

top_topic_row = valid_topic_info.iloc[0]
top_topic_name = safe_text(top_topic_row["CustomName"])
top_topic_count = int(top_topic_row["Count"])
top_topic_profile = safe_text(top_topic_row.get("ArabicProfile", "عام"))
top_topic_confidence = int(top_topic_row.get("ConfidenceScore", 0))
top_topic_conf_label = safe_text(top_topic_row.get("ConfidenceLabel", "غير معروفة"))

peak_table = topics_over_time.copy()
if not peak_table.empty:
    peak_table = peak_table.sort_values(["topic_label", "Frequency"], ascending=[True, False])
    peak_table = peak_table.groupby("topic_label", as_index=False).first()
    peak_table["PeakDate"] = pd.to_datetime(peak_table["Timestamp"]).dt.strftime("%Y-%m-%d")
    peak_table = peak_table[["topic_label", "PeakDate", "Frequency"]].rename(
        columns={
            "topic_label": "الموضوع",
            "PeakDate": "تاريخ الذروة",
            "Frequency": "أعلى تكرار",
        }
    )
else:
    peak_table = pd.DataFrame(columns=["الموضوع", "تاريخ الذروة", "أعلى تكرار"])

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("عدد التعليقات", int(summary["num_comments"]))
m2.metric("عدد المنشورات", int(summary["num_posts"]))
m3.metric("عدد المواضيع", int(num_topics))
m4.metric("الضوضاء", f"{noise_count} ({noise_ratio:.1f}%)")
m5.metric("متوسط الثقة", f"{avg_confidence:.0f}/100")

st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-label">أبرز موضوع</div>
        <div class="hero-title">{top_topic_name}</div>
        <div class="hero-grid">
            <div class="hero-mini">
                <div class="hero-mini-label">عدد التعليقات</div>
                <div class="hero-mini-value">{top_topic_count:,}</div>
            </div>
            <div class="hero-mini">
                <div class="hero-mini-label">تصنيف المجال</div>
                <div class="hero-mini-value">{top_topic_profile}</div>
            </div>
            <div class="hero-mini">
                <div class="hero-mini-label">درجة الثقة</div>
                <div class="hero-mini-value">{top_topic_confidence}/100 — {top_topic_conf_label}</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("### الخلاصة التنفيذية")
st.markdown(
    f"""
    <div class="glass-card">
        <ul class="summary-list">
            <li>تم تحليل <b>{len(sampled_df):,}</b> سجلًا، وبعد التنظيف بقي <b>{len(df2):,}</b> تعليقًا صالحًا.</li>
            <li>اكتشف النظام <b>{num_topics}</b> مواضيع رئيسية، وكان أبرزها <b>{top_topic_name}</b>.</li>
            <li>درجة الثقة في الموضوع الأبرز هي <b>{top_topic_confidence}/100</b>، ومتوسط الثقة في جميع المواضيع <b>{avg_confidence:.0f}/100</b>.</li>
            <li>الضوضاء تعني تعليقات لم تتجمع في موضوع واضح بما يكفي، وبلغت هنا <b>{noise_count:,}</b> تعليقًا، أي <b>{noise_ratio:.1f}%</b> من التعليقات النظيفة.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "نظرة عامة",
    "المواضيع",
    "أمثلة التعليقات",
    "الرسوم والتنقل",
    "تفاصيل تقنية",
])

with tab1:
    st.subheader("ملخص سريع")
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### أهم المؤشرات")
        st.write(f"- أكثر موضوع حضورًا: **{top_topic_name}**")
        st.write(f"- عدد الموضوعات المكتشفة: **{num_topics}**")
        st.write(f"- عدد الموضوعات عالية الثقة: **{high_conf_topics}**")
        st.write(f"- نسبة الضوضاء: **{noise_ratio:.1f}%**")
        st.write(f"- متوسط الثقة: **{avg_confidence:.0f}/100**")
        st.markdown('</div>', unsafe_allow_html=True)

    with right:
        render_confidence_card(top_topic_row, title="درجة الثقة في أبرز موضوع")

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("#### ذروة كل موضوع")
    st.dataframe(peak_table, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("استعراض الموضوعات")

    selected_ui_label = st.selectbox(
        "اختر موضوعًا",
        valid_topic_info["UI_Label"].tolist(),
        key="topic_overview_select",
    )

    selected_topic_row = valid_topic_info[valid_topic_info["UI_Label"] == selected_ui_label].iloc[0]
    selected_topic_id = int(selected_topic_row["Topic"])

    rep_docs = selected_topic_row.get("Representative_Docs", [])
    if isinstance(rep_docs, str):
        rep_docs = [rep_docs]
    if not isinstance(rep_docs, list):
        rep_docs = []

    clean_keywords = selected_topic_row.get("CleanKeywords", [])
    if not isinstance(clean_keywords, list):
        clean_keywords = []

    st.markdown(
        f"""
        <div class="glass-card">
            <div class="small-muted">اسم الموضوع</div>
            <div style="font-size:30px;font-weight:800;line-height:1.25;">{safe_text(selected_topic_row['CustomName'])}</div>
            <div class="topic-badge">
                Topic ID: {selected_topic_id} • العدد: {int(selected_topic_row['Count'])} • المجال: {safe_text(selected_topic_row['ArabicProfile'])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_confidence_card(selected_topic_row, title="درجة الثقة في هذا الموضوع")

    info_col1, info_col2 = st.columns(2)
    with info_col1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**الكلمات المفتاحية النظيفة**")
        if clean_keywords:
            st.write("، ".join(clean_keywords))
        else:
            st.info("لا توجد كلمات مفتاحية نظيفة كافية لهذا الموضوع.")
        st.markdown('</div>', unsafe_allow_html=True)

    with info_col2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("**تعليقات ممثلة للموضوع**")
        if rep_docs:
            for doc in rep_docs[:5]:
                st.markdown(f"- {doc}")
        else:
            st.info("لا توجد تعليقات ممثلة متاحة.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("**كل الموضوعات المكتشفة**")
    display_cols = [
        c for c in [
            "Topic",
            "Count",
            "ArabicProfile",
            "CustomName",
            "ConfidenceScore",
            "ConfidenceLabel",
            "CleanKeywords",
        ] if c in valid_topic_info.columns
    ]
    rename_map = {
        "ArabicProfile": "المجال",
        "CustomName": "اسم الموضوع",
        "ConfidenceScore": "الدرجة",
        "ConfidenceLabel": "مستوى الثقة",
        "CleanKeywords": "الكلمات المفتاحية"
    }
    st.dataframe(valid_topic_info[display_cols].rename(columns=rename_map), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab3:
    st.subheader("عينات التعليقات")

    selected_ui_label_examples = st.selectbox(
        "اختر موضوعًا لعرض تعليقاته",
        valid_topic_info["UI_Label"].tolist(),
        key="examples_select",
    )

    selected_topic_row_examples = valid_topic_info[valid_topic_info["UI_Label"] == selected_ui_label_examples].iloc[0]
    selected_topic_id_examples = int(selected_topic_row_examples["Topic"])

    examples = df_valid[df_valid["topic"] == selected_topic_id_examples].copy()
    examples = examples.sort_values("date", ascending=False).head(10)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.write(f"عدد التعليقات ضمن هذا الموضوع: {int(selected_topic_row_examples['Count'])}")

    show_cols = [c for c in ["date", "text", "topic_label", "post_id_true"] if c in examples.columns]
    rename_map = {
        "date": "التاريخ",
        "text": "التعليق",
        "topic_label": "اسم الموضوع",
        "post_id_true": "معرف المنشور",
    }

    st.dataframe(
        examples[show_cols].rename(columns=rename_map),
        use_container_width=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with tab4:
    st.subheader("الرسوم والتنقل")

    min_available_date = pd.to_datetime(df_valid["date"]).min().date()
    max_available_date = pd.to_datetime(df_valid["date"]).max().date()

    selected_range = st.date_input(
        "اختر الفترة الزمنية التي تريد أن تُحسب الرسوم داخلها",
        value=(min_available_date, max_available_date),
        min_value=min_available_date,
        max_value=max_available_date,
        key="charts_date_range",
    )

    if not isinstance(selected_range, (list, tuple)) or len(selected_range) != 2:
        st.info("اختر تاريخ بداية وتاريخ نهاية لعرض الرسوم.")
    else:
        start_date, end_date = selected_range

        filtered_df_valid = df_valid[
            (pd.to_datetime(df_valid["date"]).dt.date >= start_date) &
            (pd.to_datetime(df_valid["date"]).dt.date <= end_date)
        ].copy()

        st.caption(
            f"جميع الرسوم في هذا التبويب محسوبة فقط للفترة من {start_date} إلى {end_date}."
        )

        if filtered_df_valid.empty:
            st.warning("لا توجد بيانات في الفترة الزمنية المحددة.")
        else:
            if "month" in filtered_df_valid.columns:
                filtered_df_valid["Timestamp"] = pd.to_datetime(
                    filtered_df_valid["month"].astype(str) + "-01",
                    errors="coerce",
                )
            else:
                filtered_df_valid["Timestamp"] = pd.to_datetime(
                    filtered_df_valid["date"]
                ).dt.to_period("M").dt.to_timestamp()

            filtered_topics_over_time = (
                filtered_df_valid
                .groupby(["topic", "topic_label", "Timestamp"], as_index=False)
                .size()
                .rename(columns={"topic": "Topic", "size": "Frequency"})
                .sort_values(["topic_label", "Timestamp"])
            )

            topic_counts = (
                filtered_df_valid
                .groupby(["topic", "topic_label"], as_index=False)
                .size()
                .rename(columns={"topic": "Topic", "size": "Count"})
            )

            meta_cols = [c for c in valid_topic_info.columns if c not in ["Count", "UI_Label"]]

            filtered_valid_topic_info = topic_counts.merge(
                valid_topic_info[meta_cols].drop_duplicates(subset=["Topic"]),
                on="Topic",
                how="left",
            )

            filtered_valid_topic_info["CustomName"] = filtered_valid_topic_info["CustomName"].fillna(
                filtered_valid_topic_info["topic_label"]
            )

            filtered_valid_topic_info = (
                filtered_valid_topic_info
                .sort_values("Count", ascending=False)
                .reset_index(drop=True)
            )

            if filtered_valid_topic_info.empty:
                st.warning("لا توجد مواضيع ظاهرة داخل الفترة المحددة.")
            else:
                render_chart_panel(
                    valid_topic_info=filtered_valid_topic_info,
                    topics_over_time=filtered_topics_over_time,
                    top_n=top_n_charts,
                )

                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("### ملخص الفترة المحددة")
                s1, s2, s3 = st.columns(3)
                s1.metric("التعليقات في هذه الفترة", len(filtered_df_valid))
                s2.metric("المواضيع الظاهرة", filtered_valid_topic_info["Topic"].nunique())
                s3.metric("أكبر موضوع في الفترة", safe_text(filtered_valid_topic_info.iloc[0]["CustomName"]))
                st.markdown('</div>', unsafe_allow_html=True)

with tab5:
    with st.expander("بيانات بعد التنظيف", expanded=False):
        st.write(f"Shape after preprocessing: {df2.shape}")
        cols_to_show = [c for c in ["text", "normalized_text", "clean_text", "post_id_true"] if c in df2.columns]
        st.dataframe(df2[cols_to_show].head(10), use_container_width=True)

    with st.expander("الجدول الداخلي للمواضيع", expanded=False):
        cols_to_show = [
            c for c in [
                "Topic",
                "Count",
                "ArabicProfile",
                "Name",
                "CustomName",
                "ConfidenceScore",
                "ConfidenceLabel",
                "ConfidenceReason",
                "CleanKeywords",
                "Representative_Docs",
            ] if c in topic_info_display.columns
        ]
        rename_map = {
            "ArabicProfile": "المجال",
            "CustomName": "اسم الموضوع",
            "ConfidenceScore": "الدرجة",
            "ConfidenceLabel": "مستوى الثقة",
            "ConfidenceReason": "سبب الدرجة",
            "CleanKeywords": "الكلمات المفتاحية",
            "Representative_Docs": "تعليقات ممثلة"
        }
        st.dataframe(topic_info_display[cols_to_show].rename(columns=rename_map), use_container_width=True)

    with st.expander("عينات البيانات الصالحة", expanded=False):
        cols_to_show = [c for c in ["date", "month", "text", "topic", "topic_label", "post_id_true"] if c in df_valid.columns]
        st.dataframe(df_valid[cols_to_show].head(15), use_container_width=True)

    with st.expander("التصدير", expanded=False):
        st.download_button(
            "تنزيل topic_info_display.csv",
            data=topic_info_display.to_csv(index=False).encode("utf-8-sig"),
            file_name="topic_info_display.csv",
            mime="text/csv",
        )

        st.download_button(
            "تنزيل df_valid.csv",
            data=df_valid.to_csv(index=False).encode("utf-8-sig"),
            file_name="df_valid.csv",
            mime="text/csv",
        )

        st.download_button(
            "تنزيل topics_over_time.csv",
            data=topics_over_time.to_csv(index=False).encode("utf-8-sig"),
            file_name="topics_over_time.csv",
            mime="text/csv",
        )
