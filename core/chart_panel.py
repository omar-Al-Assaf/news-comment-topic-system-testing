import streamlit as st

from core.visualization import (
    build_google_trends_style_chart,
    build_topic_comparison_chart,
    build_topic_distribution_bar,
    build_topic_distribution_donut,
    build_topic_treemap,
    build_heatmap,
    build_area_chart,
    build_topic_peak_bar
)


def render_chart_panel(valid_topic_info, topics_over_time, top_n=8):
    chart_options = [
        "مؤشر موضوع واحد — Google Trends Style",
        "مقارنة عدة مواضيع",
        "توزيع المواضيع — أعمدة",
        "توزيع المواضيع — دائري",
        "خريطة شجرية",
        "خريطة حرارية",
        "اتجاهات تراكمية",
        "قمم المواضيع"
    ]

    selected_chart = st.selectbox(
        "اختر نوع الرسم المراد عرضه",
        chart_options,
        key="selected_chart_type"
    )

    topic_labels = valid_topic_info["CustomName"].tolist()

    if selected_chart == "مؤشر موضوع واحد — Google Trends Style":
        st.caption("رسم مبسط يوضح صعود الموضوع وهبوطه زمنيًا بشكل قريب من Google Trends.")
        selected_topic = st.selectbox(
            "اختر موضوعًا",
            topic_labels,
            key="single_topic_chart_select"
        )
        normalize = st.checkbox(
            "عرض كمؤشر نسبي من 0 إلى 100",
            value=True,
            key="single_topic_chart_normalize"
        )

        st.plotly_chart(
            build_google_trends_style_chart(
                topics_over_time,
                selected_topic_label=selected_topic,
                normalize=normalize
            ),
            use_container_width=True,
            key="google_trends_style_chart"
        )

    elif selected_chart == "مقارنة عدة مواضيع":
        st.caption("مفيد لرؤية أي موضوع كان أكثر صعودًا ومتى ظهرت ذروته مقارنة بغيره.")
        default_topics = topic_labels[:min(3, len(topic_labels))]
        selected_topics = st.multiselect(
            "اختر موضوعين أو أكثر",
            topic_labels,
            default=default_topics,
            key="multi_topic_chart_select"
        )
        normalize = st.checkbox(
            "تطبيع القيم إلى 0-100",
            value=True,
            key="multi_topic_chart_normalize"
        )

        if selected_topics:
            st.plotly_chart(
                build_topic_comparison_chart(
                    topics_over_time,
                    selected_topics=selected_topics,
                    normalize=normalize
                ),
                use_container_width=True,
                key="multi_topic_comparison_chart"
            )
        else:
            st.info("اختر موضوعًا واحدًا على الأقل.")

    elif selected_chart == "توزيع المواضيع — أعمدة":
        st.caption("يبين أكثر المواضيع حضورًا في العينة الحالية.")
        st.plotly_chart(
            build_topic_distribution_bar(valid_topic_info, top_n=top_n),
            use_container_width=True,
            key="topic_distribution_bar_chart"
        )

    elif selected_chart == "توزيع المواضيع — دائري":
        st.caption("يوضح حصة كل موضوع بشكل مبسط جدًا للمستخدم غير التقني.")
        st.plotly_chart(
            build_topic_distribution_donut(valid_topic_info, top_n=top_n),
            use_container_width=True,
            key="topic_distribution_donut_chart"
        )

    elif selected_chart == "خريطة شجرية":
        st.caption("تقسيم مرئي بحسب الـ profile ثم الموضوع، مناسب للنظرة الهيكلية السريعة.")
        st.plotly_chart(
            build_topic_treemap(valid_topic_info, top_n=max(top_n, 10)),
            use_container_width=True,
            key="topic_treemap_chart"
        )

    elif selected_chart == "خريطة حرارية":
        st.caption("تعرض كثافة كل موضوع عبر الفترات الزمنية بشكل متقاطع.")
        st.plotly_chart(
            build_heatmap(topics_over_time),
            use_container_width=True,
            key="topic_heatmap_chart"
        )

    elif selected_chart == "اتجاهات تراكمية":
        st.caption("توضح كيف تتوزع المواضيع مع الزمن كمساحات متراكمة.")
        st.plotly_chart(
            build_area_chart(topics_over_time),
            use_container_width=True,
            key="topic_area_chart"
        )

    elif selected_chart == "قمم المواضيع":
        st.caption("يبين أعلى نقطة وصل إليها كل موضوع، وهو سهل جدًا للفهم في العرض.")
        st.plotly_chart(
            build_topic_peak_bar(topics_over_time),
            use_container_width=True,
            key="topic_peak_bar_chart"
        )
