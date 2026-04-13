import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

PALETTE = [
    "#5AA9FF", "#8A7CFF", "#2DD4BF", "#F59E0B",
    "#EF4444", "#EC4899", "#22C55E", "#A855F7",
    "#06B6D4", "#F97316"
]


def _apply_dark_theme(fig, height=560):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        font=dict(size=14),
        margin=dict(l=30, r=30, t=70, b=40),
        legend_title_text="",
        height=height
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(255,255,255,0.08)",
        zeroline=False
    )
    return fig


def build_google_trends_style_chart(topics_over_time, selected_topic_label, normalize=True):
    data = topics_over_time.copy()
    data = data[data["topic_label"] == selected_topic_label].copy()
    data = data.sort_values("Timestamp")

    if data.empty:
        fig = go.Figure()
        fig.update_layout(title="لا توجد بيانات لهذا الموضوع")
        return _apply_dark_theme(fig)

    if normalize:
        max_val = data["Frequency"].max()
        data["PlotValue"] = (data["Frequency"] / max_val) * 100 if max_val > 0 else 0
        y_title = "مؤشر الاهتمام النسبي (0-100)"
    else:
        data["PlotValue"] = data["Frequency"]
        y_title = "عدد التعليقات"

    peak_row = data.loc[data["PlotValue"].idxmax()]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["Timestamp"],
            y=data["PlotValue"],
            mode="lines+markers",
            line=dict(color=PALETTE[0], width=4, shape="spline", smoothing=0.5),
            marker=dict(size=7, color="#C7E7FF"),
            fill="tozeroy",
            fillcolor="rgba(90,169,255,0.16)",
            hovertemplate="<b>%{x}</b><br>القيمة: %{y:.1f}<extra></extra>"
        )
    )

    fig.add_annotation(
        x=peak_row["Timestamp"],
        y=peak_row["PlotValue"],
        text="ذروة",
        showarrow=True,
        arrowhead=2,
        ax=0,
        ay=-45
    )

    fig.update_layout(
        title=f"تطور الموضوع عبر الزمن — {selected_topic_label}",
        xaxis_title="الزمن",
        yaxis_title=y_title
    )

    if normalize:
        fig.update_yaxes(range=[0, 105])

    return _apply_dark_theme(fig)


def build_topic_comparison_chart(topics_over_time, selected_topics, normalize=True):
    data = topics_over_time.copy()
    data = data[data["topic_label"].isin(selected_topics)].copy()
    data = data.sort_values("Timestamp")

    if data.empty:
        fig = go.Figure()
        fig.update_layout(title="لا توجد بيانات للمقارنة")
        return _apply_dark_theme(fig)

    if normalize:
        data["PlotValue"] = data.groupby("topic_label")["Frequency"].transform(
            lambda s: (s / s.max()) * 100 if s.max() > 0 else 0
        )
        y_title = "مؤشر الاهتمام النسبي (0-100)"
    else:
        data["PlotValue"] = data["Frequency"]
        y_title = "عدد التعليقات"

    fig = px.line(
        data,
        x="Timestamp",
        y="PlotValue",
        color="topic_label",
        markers=True,
        color_discrete_sequence=PALETTE,
        title="مقارنة عدة مواضيع عبر الزمن"
    )

    fig.update_traces(line=dict(width=3))
    fig.update_layout(
        xaxis_title="الزمن",
        yaxis_title=y_title
    )

    if normalize:
        fig.update_yaxes(range=[0, 105])

    return _apply_dark_theme(fig)


def build_topic_distribution_bar(valid_topic_info, top_n=8):
    data = valid_topic_info.copy().head(top_n).sort_values("Count", ascending=True)

    fig = px.bar(
        data,
        x="Count",
        y="CustomName",
        orientation="h",
        color="CustomName",
        color_discrete_sequence=PALETTE,
        text="Count",
        title="أكثر المواضيع من حيث عدد التعليقات"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="عدد التعليقات",
        yaxis_title="",
        showlegend=False
    )

    return _apply_dark_theme(fig)


def build_topic_distribution_donut(valid_topic_info, top_n=8):
    data = valid_topic_info.copy().head(top_n)

    fig = px.pie(
        data,
        names="CustomName",
        values="Count",
        hole=0.58,
        color_discrete_sequence=PALETTE,
        title="حصة كل موضوع من إجمالي المواضيع الظاهرة"
    )

    return _apply_dark_theme(fig)


def build_topic_treemap(valid_topic_info, top_n=12):
    data = valid_topic_info.copy().head(top_n)

    fig = px.treemap(
        data,
        path=["DetectedProfile", "CustomName"],
        values="Count",
        color="Count",
        color_continuous_scale="Blues",
        title="خريطة شجرية للمواضيع"
    )

    return _apply_dark_theme(fig)


def build_heatmap(topics_over_time):
    data = topics_over_time.copy()
    pivot = data.pivot_table(
        index="topic_label",
        columns="Timestamp",
        values="Frequency",
        aggfunc="sum",
        fill_value=0
    )

    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale="Blues",
            hoverongaps=False
        )
    )

    fig.update_layout(
        title="خريطة حرارية لتكرار المواضيع عبر الزمن",
        xaxis_title="الزمن",
        yaxis_title="الموضوع"
    )

    return _apply_dark_theme(fig, height=620)


def build_area_chart(topics_over_time):
    data = topics_over_time.copy().sort_values("Timestamp")

    fig = px.area(
        data,
        x="Timestamp",
        y="Frequency",
        color="topic_label",
        color_discrete_sequence=PALETTE,
        title="اتجاهات المواضيع التراكمية عبر الزمن"
    )

    fig.update_layout(
        xaxis_title="الزمن",
        yaxis_title="عدد التعليقات"
    )

    return _apply_dark_theme(fig)


def build_topic_peak_bar(topics_over_time):
    data = topics_over_time.copy()
    peaks = data.sort_values(["topic_label", "Frequency"], ascending=[True, False])
    peaks = peaks.groupby("topic_label", as_index=False).first()
    peaks = peaks.sort_values("Frequency", ascending=True)

    fig = px.bar(
        peaks,
        x="Frequency",
        y="topic_label",
        orientation="h",
        color="topic_label",
        color_discrete_sequence=PALETTE,
        text="Frequency",
        title="ذروة كل موضوع"
    )

    fig.update_traces(textposition="outside")
    fig.update_layout(
        xaxis_title="أعلى تكرار",
        yaxis_title="",
        showlegend=False
    )

    return _apply_dark_theme(fig)
