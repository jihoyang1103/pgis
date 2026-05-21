import io
from datetime import date, timedelta

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Streamlit Migration App",
    page_icon=":bar_chart:",
    layout="wide",
    initial_sidebar_state="expanded",
)


CUSTOM_CSS = """
<style>
    :root {
        --bg: #f7f8f4;
        --ink: #17211b;
        --muted: #66736b;
        --line: #dfe5dc;
        --panel: #ffffff;
        --accent: #0f766e;
        --accent-soft: #d9f3ee;
        --coral: #e76f51;
        --gold: #d69e2e;
    }

    .stApp {
        background:
            linear-gradient(180deg, rgba(247, 248, 244, 0.96), rgba(247, 248, 244, 1)),
            radial-gradient(circle at 10% 20%, rgba(15, 118, 110, 0.10), transparent 26%),
            radial-gradient(circle at 86% 8%, rgba(231, 111, 81, 0.10), transparent 24%);
        color: var(--ink);
    }

    [data-testid="stSidebar"] {
        background: #eef3ed;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--ink);
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }

    .app-hero {
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.82);
        border-radius: 8px;
        padding: 1.35rem 1.45rem;
        box-shadow: 0 18px 45px rgba(23, 33, 27, 0.08);
    }

    .eyebrow {
        color: var(--accent);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0;
        text-transform: uppercase;
        margin-bottom: 0.3rem;
    }

    .hero-title {
        color: var(--ink);
        font-size: 2.25rem;
        line-height: 1.08;
        font-weight: 800;
        margin: 0;
    }

    .hero-copy {
        color: var(--muted);
        font-size: 0.98rem;
        margin: 0.55rem 0 0;
        max-width: 760px;
    }

    .metric-card {
        border: 1px solid var(--line);
        background: var(--panel);
        border-radius: 8px;
        padding: 1rem 1rem 0.95rem;
        min-height: 112px;
        box-shadow: 0 14px 32px rgba(23, 33, 27, 0.06);
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }

    .metric-value {
        color: var(--ink);
        font-size: 1.75rem;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 0.25rem;
    }

    .metric-delta {
        color: var(--accent);
        font-size: 0.8rem;
        font-weight: 700;
    }

    .section-title {
        color: var(--ink);
        font-size: 1.2rem;
        font-weight: 800;
        margin: 1.15rem 0 0.45rem;
    }

    div[data-testid="stMetric"] {
        border: 1px solid var(--line);
        background: #ffffff;
        border-radius: 8px;
        padding: 0.85rem 0.95rem;
        box-shadow: 0 12px 28px rgba(23, 33, 27, 0.05);
    }

    div[data-testid="stMetricLabel"] p {
        color: var(--muted);
        font-weight: 700;
    }

    div[data-testid="stMetricValue"] {
        color: var(--ink);
    }

    div[data-testid="stTabs"] button {
        font-weight: 700;
    }

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 8px;
        border: 1px solid var(--accent);
        background: var(--accent);
        color: white;
        font-weight: 700;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: #115e59;
        background: #115e59;
        color: white;
    }

    [data-testid="stDataFrame"],
    [data-testid="stDataEditor"] {
        border: 1px solid var(--line);
        border-radius: 8px;
        overflow: hidden;
    }

    @media (max-width: 760px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero-title {
            font-size: 1.55rem;
        }

        .app-hero {
            padding: 1rem;
        }
    }
</style>
"""


@st.cache_data(show_spinner=False)
def create_sample_data(days: int = 120) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    dates = pd.date_range(start_date, end_date, freq="D")
    channels = ["Direct", "Search", "Social", "Email", "Partner"]
    regions = ["Seoul", "Busan", "Incheon", "Daegu", "Daejeon"]

    rows = []
    for current in dates:
        weekday_boost = 1.14 if current.weekday() < 5 else 0.86
        seasonal = 1 + 0.12 * np.sin(len(rows) / 9)
        for channel in channels:
            for region in regions:
                channel_weight = {
                    "Direct": 1.08,
                    "Search": 1.22,
                    "Social": 0.94,
                    "Email": 0.78,
                    "Partner": 0.68,
                }[channel]
                region_weight = {
                    "Seoul": 1.24,
                    "Busan": 0.96,
                    "Incheon": 0.88,
                    "Daegu": 0.78,
                    "Daejeon": 0.70,
                }[region]
                visitors = int(
                    rng.normal(540, 80)
                    * weekday_boost
                    * seasonal
                    * channel_weight
                    * region_weight
                )
                conversion_rate = np.clip(
                    rng.normal(0.058, 0.014)
                    * (1.08 if channel in ["Search", "Email"] else 1.0),
                    0.012,
                    0.13,
                )
                orders = int(visitors * conversion_rate)
                revenue = int(orders * rng.normal(74_000, 9_000))
                cost = int(visitors * rng.normal(690, 120) * (1.25 if channel == "Social" else 1))
                satisfaction = round(float(np.clip(rng.normal(4.2, 0.35), 2.8, 5.0)), 2)

                rows.append(
                    {
                        "date": current.date(),
                        "region": region,
                        "channel": channel,
                        "visitors": max(visitors, 0),
                        "orders": max(orders, 0),
                        "revenue": max(revenue, 0),
                        "cost": max(cost, 0),
                        "satisfaction": satisfaction,
                    }
                )

    data = pd.DataFrame(rows)
    data["profit"] = data["revenue"] - data["cost"]
    data["conversion"] = np.where(data["visitors"] > 0, data["orders"] / data["visitors"], 0)
    return data


def normalize_columns(data: pd.DataFrame) -> pd.DataFrame:
    cleaned = data.copy()
    cleaned.columns = [str(column).strip().lower().replace(" ", "_") for column in cleaned.columns]

    if "date" not in cleaned.columns:
        date_candidates = [
            column
            for column in cleaned.columns
            if "date" in column or "day" in column or "created" in column
        ]
        if date_candidates:
            cleaned = cleaned.rename(columns={date_candidates[0]: "date"})

    if "date" in cleaned.columns:
        cleaned["date"] = pd.to_datetime(cleaned["date"], errors="coerce").dt.date
        cleaned = cleaned.dropna(subset=["date"])

    numeric_columns = ["visitors", "orders", "revenue", "cost", "profit", "conversion", "satisfaction"]
    for column in numeric_columns:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce").fillna(0)

    if "revenue" in cleaned.columns and "cost" in cleaned.columns and "profit" not in cleaned.columns:
        cleaned["profit"] = cleaned["revenue"] - cleaned["cost"]

    if "orders" in cleaned.columns and "visitors" in cleaned.columns and "conversion" not in cleaned.columns:
        cleaned["conversion"] = np.where(cleaned["visitors"] > 0, cleaned["orders"] / cleaned["visitors"], 0)

    if "region" not in cleaned.columns:
        cleaned["region"] = "All"

    if "channel" not in cleaned.columns:
        cleaned["channel"] = "All"

    return cleaned


def load_uploaded_data(uploaded_file) -> pd.DataFrame:
    if uploaded_file is None:
        return create_sample_data()

    suffix = uploaded_file.name.lower().split(".")[-1]
    if suffix == "csv":
        data = pd.read_csv(uploaded_file)
    elif suffix in {"xlsx", "xls"}:
        data = pd.read_excel(uploaded_file)
    else:
        st.warning("CSV 또는 Excel 파일만 사용할 수 있어 샘플 데이터를 표시합니다.")
        return create_sample_data()

    return normalize_columns(data)


def format_currency(value: float) -> str:
    if abs(value) >= 100_000_000:
        return f"{value / 100_000_000:.1f}억"
    if abs(value) >= 10_000:
        return f"{value / 10_000:.1f}만"
    return f"{value:,.0f}"


def format_percent(value: float) -> str:
    return f"{value * 100:.1f}%"


def metric_delta(current: float, previous: float, formatter) -> str:
    if previous == 0:
        return "비교 기준 없음"
    change = (current - previous) / abs(previous)
    sign = "+" if change >= 0 else ""
    return f"{sign}{change * 100:.1f}% vs 이전 기간"


def split_current_previous(data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if data.empty or "date" not in data.columns:
        return data, data.iloc[0:0]

    sorted_dates = sorted(pd.to_datetime(data["date"]).dt.date.unique())
    midpoint = max(1, len(sorted_dates) // 2)
    previous_dates = set(sorted_dates[:midpoint])
    current_dates = set(sorted_dates[midpoint:])
    if not current_dates:
        current_dates = set(sorted_dates)
        previous_dates = set()

    return data[data["date"].isin(current_dates)], data[data["date"].isin(previous_dates)]


def safe_sum(data: pd.DataFrame, column: str) -> float:
    return float(data[column].sum()) if column in data.columns else 0.0


def safe_mean(data: pd.DataFrame, column: str) -> float:
    return float(data[column].mean()) if column in data.columns and not data.empty else 0.0


def build_line_chart(data: pd.DataFrame, metric: str) -> alt.Chart:
    daily = data.groupby("date", as_index=False)[metric].sum()
    return (
        alt.Chart(daily)
        .mark_line(color="#0f766e", strokeWidth=3)
        .encode(
            x=alt.X("date:T", title=None),
            y=alt.Y(f"{metric}:Q", title=None),
            tooltip=[
                alt.Tooltip("date:T", title="Date"),
                alt.Tooltip(f"{metric}:Q", title=metric.title(), format=",.0f"),
            ],
        )
        .properties(height=320)
    )


def build_bar_chart(data: pd.DataFrame, dimension: str, metric: str) -> alt.Chart:
    grouped = data.groupby(dimension, as_index=False)[metric].sum().sort_values(metric, ascending=False)
    return (
        alt.Chart(grouped)
        .mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4, color="#e76f51")
        .encode(
            x=alt.X(f"{dimension}:N", title=None, sort="-y"),
            y=alt.Y(f"{metric}:Q", title=None),
            tooltip=[
                alt.Tooltip(f"{dimension}:N", title=dimension.title()),
                alt.Tooltip(f"{metric}:Q", title=metric.title(), format=",.0f"),
            ],
        )
        .properties(height=320)
    )


def build_scatter_chart(data: pd.DataFrame) -> alt.Chart:
    needed = {"visitors", "orders", "revenue", "channel"}
    if not needed.issubset(data.columns):
        return alt.Chart(pd.DataFrame({"x": [], "y": []})).mark_point()

    grouped = data.groupby(["channel", "region"], as_index=False).agg(
        visitors=("visitors", "sum"),
        orders=("orders", "sum"),
        revenue=("revenue", "sum"),
    )
    return (
        alt.Chart(grouped)
        .mark_circle(opacity=0.82)
        .encode(
            x=alt.X("visitors:Q", title="Visitors"),
            y=alt.Y("orders:Q", title="Orders"),
            size=alt.Size("revenue:Q", title="Revenue", scale=alt.Scale(range=[90, 900])),
            color=alt.Color("channel:N", title="Channel"),
            tooltip=[
                alt.Tooltip("region:N", title="Region"),
                alt.Tooltip("channel:N", title="Channel"),
                alt.Tooltip("visitors:Q", title="Visitors", format=",.0f"),
                alt.Tooltip("orders:Q", title="Orders", format=",.0f"),
                alt.Tooltip("revenue:Q", title="Revenue", format=",.0f"),
            ],
        )
        .properties(height=320)
    )


def to_excel(data: pd.DataFrame) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        data.to_excel(writer, index=False, sheet_name="data")
    return buffer.getvalue()


st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

with st.sidebar:
    st.title("Control Center")
    st.caption("CSV 또는 Excel 데이터를 올리면 동일한 화면에서 즉시 분석됩니다.")
    uploaded_file = st.file_uploader("데이터 업로드", type=["csv", "xlsx", "xls"])

    data = load_uploaded_data(uploaded_file)

    if data.empty or "date" not in data.columns:
        st.error("분석하려면 date 컬럼이 필요합니다.")
        st.stop()

    min_date = min(data["date"])
    max_date = max(data["date"])
    selected_dates = st.date_input(
        "기간",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date, end_date = min_date, max_date

    regions = sorted(data["region"].dropna().unique().tolist())
    channels = sorted(data["channel"].dropna().unique().tolist())
    selected_regions = st.multiselect("지역", regions, default=regions)
    selected_channels = st.multiselect("채널", channels, default=channels)

    metric_options = [
        column
        for column in ["revenue", "profit", "orders", "visitors", "cost"]
        if column in data.columns
    ]
    selected_metric = st.selectbox("핵심 지표", metric_options, index=0)

    st.divider()
    compact_mode = st.toggle("컴팩트 보기", value=False)


filtered = data[
    (data["date"] >= start_date)
    & (data["date"] <= end_date)
    & (data["region"].isin(selected_regions))
    & (data["channel"].isin(selected_channels))
].copy()

if filtered.empty:
    st.warning("선택한 조건에 맞는 데이터가 없습니다. 필터를 조정해 주세요.")
    st.stop()

current_period, previous_period = split_current_previous(filtered)

st.markdown(
    """
    <div class="app-hero">
        <div class="eyebrow">Streamlit Migration</div>
        <h1 class="hero-title">운영 지표 대시보드</h1>
        <p class="hero-copy">
            업로드, 필터링, 차트, 데이터 편집, 다운로드 흐름을 한 화면에 모았습니다.
            원본 프로젝트 없이도 바로 실행할 수 있는 Streamlit 앱입니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

metric_cols = st.columns(4)
revenue = safe_sum(current_period, "revenue")
prev_revenue = safe_sum(previous_period, "revenue")
orders = safe_sum(current_period, "orders")
prev_orders = safe_sum(previous_period, "orders")
visitors = safe_sum(current_period, "visitors")
prev_visitors = safe_sum(previous_period, "visitors")
conversion = orders / visitors if visitors else 0
prev_conversion = prev_orders / prev_visitors if prev_visitors else 0
profit = safe_sum(current_period, "profit")
prev_profit = safe_sum(previous_period, "profit")

metric_cols[0].metric("매출", format_currency(revenue), metric_delta(revenue, prev_revenue, format_currency))
metric_cols[1].metric("주문", f"{orders:,.0f}", metric_delta(orders, prev_orders, lambda value: f"{value:,.0f}"))
metric_cols[2].metric("전환율", format_percent(conversion), metric_delta(conversion, prev_conversion, format_percent))
metric_cols[3].metric("이익", format_currency(profit), metric_delta(profit, prev_profit, format_currency))

overview_tab, detail_tab, editor_tab = st.tabs(["Overview", "Detail", "Data"])

with overview_tab:
    left, right = st.columns((1.35, 1))
    with left:
        st.markdown('<div class="section-title">기간별 추세</div>', unsafe_allow_html=True)
        st.altair_chart(build_line_chart(filtered, selected_metric), use_container_width=True)
    with right:
        st.markdown('<div class="section-title">채널 성과</div>', unsafe_allow_html=True)
        st.altair_chart(build_bar_chart(filtered, "channel", selected_metric), use_container_width=True)

    if not compact_mode:
        st.markdown('<div class="section-title">방문자와 주문 관계</div>', unsafe_allow_html=True)
        st.altair_chart(build_scatter_chart(filtered), use_container_width=True)

with detail_tab:
    dimension = st.radio("분석 기준", options=["region", "channel"], horizontal=True)
    summary = (
        filtered.groupby(dimension, as_index=False)
        .agg(
            visitors=("visitors", "sum"),
            orders=("orders", "sum"),
            revenue=("revenue", "sum"),
            cost=("cost", "sum"),
            profit=("profit", "sum"),
            satisfaction=("satisfaction", "mean"),
        )
        .sort_values("revenue", ascending=False)
    )
    summary["conversion"] = np.where(summary["visitors"] > 0, summary["orders"] / summary["visitors"], 0)

    st.dataframe(
        summary,
        use_container_width=True,
        hide_index=True,
        column_config={
            "revenue": st.column_config.NumberColumn("revenue", format="%,d"),
            "cost": st.column_config.NumberColumn("cost", format="%,d"),
            "profit": st.column_config.NumberColumn("profit", format="%,d"),
            "conversion": st.column_config.ProgressColumn(
                "conversion",
                format="%.1f%%",
                min_value=0,
                max_value=max(float(summary["conversion"].max()), 0.12),
            ),
            "satisfaction": st.column_config.NumberColumn("satisfaction", format="%.2f"),
        },
    )

    st.download_button(
        "Excel 다운로드",
        data=to_excel(summary),
        file_name="streamlit_dashboard_summary.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

with editor_tab:
    st.markdown('<div class="section-title">데이터 편집</div>', unsafe_allow_html=True)
    edited = st.data_editor(
        filtered.sort_values("date", ascending=False),
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        column_config={
            "date": st.column_config.DateColumn("date"),
            "region": st.column_config.TextColumn("region"),
            "channel": st.column_config.TextColumn("channel"),
            "visitors": st.column_config.NumberColumn("visitors", min_value=0, step=1),
            "orders": st.column_config.NumberColumn("orders", min_value=0, step=1),
            "revenue": st.column_config.NumberColumn("revenue", min_value=0, step=1000),
            "cost": st.column_config.NumberColumn("cost", min_value=0, step=1000),
            "satisfaction": st.column_config.NumberColumn("satisfaction", min_value=0.0, max_value=5.0, step=0.1),
        },
    )

    download_cols = st.columns([1, 1, 4])
    with download_cols[0]:
        st.download_button(
            "CSV",
            data=edited.to_csv(index=False).encode("utf-8-sig"),
            file_name="streamlit_dashboard_data.csv",
            mime="text/csv",
        )
    with download_cols[1]:
        st.download_button(
            "Excel",
            data=to_excel(edited),
            file_name="streamlit_dashboard_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
