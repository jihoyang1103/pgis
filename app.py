from __future__ import annotations

import html
import json
import math
import re
import urllib.parse
import urllib.request

import pandas as pd
import pydeck as pdk
import streamlit as st


st.set_page_config(
    page_title="월세 생존 지도",
    page_icon="map",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    :root {
        color-scheme: light;
        --paper: #f7f5ef;
        --ink: #20252b;
        --muted: #6b7280;
        --line: #e2ded3;
        --line-soft: #ece8dd;
        --surface: #ffffff;
        --surface-alt: #fbfaf6;
        --chip-bg: #f0ece2;
        --note-bg: #f3f8fa;
        --note-ink: #26323a;
        --warning-bg: #fff5f3;
        --warning-ink: #4b2f2d;
        --input-bg: #ffffff;
        --input-ink: #20252b;
        --green: #239d72;
        --yellow: #d9982f;
        --red: #d95f5f;
        --blue: #2f6f9f;
        --shadow: 0 1px 2px rgba(32, 37, 43, 0.05);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            color-scheme: dark;
            --paper: #0f1216;
            --ink: #f0f3f6;
            --muted: #a8b0ba;
            --line: #2b3139;
            --line-soft: #242a32;
            --surface: #171b21;
            --surface-alt: #1d232b;
            --chip-bg: #252c35;
            --note-bg: #142231;
            --note-ink: #d7e7f5;
            --warning-bg: #2a1a1d;
            --warning-ink: #f5d1cf;
            --input-bg: #11161c;
            --input-ink: #f0f3f6;
            --green: #3ecf98;
            --yellow: #e7b75b;
            --red: #ef7d7d;
            --blue: #74aee8;
            --shadow: 0 1px 2px rgba(0, 0, 0, 0.38);
        }
    }

    html, body, .stApp {
        background: var(--paper);
        color: var(--ink);
    }

    .stApp p,
    .stApp label,
    .stApp span,
    .stApp [data-testid="stMarkdownContainer"] {
        color: inherit;
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
        max-width: 1240px;
    }

    [data-testid="stSidebar"] {
        background: var(--surface);
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] * {
        color: var(--ink);
    }

    h1, h2, h3 {
        letter-spacing: 0;
        color: var(--ink);
    }

    .hero {
        padding: 0.2rem 0 1rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1rem;
    }

    .hero h1 {
        font-size: clamp(2rem, 4vw, 3.6rem);
        line-height: 1.05;
        margin: 0 0 0.5rem;
        color: var(--ink);
    }

    .hero p {
        max-width: 790px;
        color: var(--muted);
        font-size: 1.02rem;
        line-height: 1.65;
        margin: 0;
    }

    .metric-card {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem;
        min-height: 112px;
        box-shadow: var(--shadow);
    }

    .metric-card small {
        display: block;
        color: var(--muted);
        font-size: 0.78rem;
        margin-bottom: 0.35rem;
    }

    .metric-card strong {
        display: block;
        font-size: 1.7rem;
        line-height: 1.1;
        color: var(--ink);
    }

    .metric-card span {
        display: block;
        color: var(--muted);
        font-size: 0.82rem;
        margin-top: 0.45rem;
    }

    .panel {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: var(--shadow);
    }

    .rank-row {
        display: grid;
        grid-template-columns: 2.2rem 1fr auto;
        gap: 0.75rem;
        align-items: center;
        padding: 0.8rem 0;
        border-bottom: 1px solid var(--line-soft);
    }

    .rank-row:last-child {
        border-bottom: 0;
    }

    .rank-num {
        width: 2rem;
        height: 2rem;
        display: grid;
        place-items: center;
        border-radius: 50%;
        background: var(--chip-bg);
        font-weight: 700;
        color: var(--ink);
    }

    .rank-title {
        font-weight: 700;
        color: var(--ink);
        margin-bottom: 0.15rem;
    }

    .rank-meta {
        color: var(--muted);
        font-size: 0.84rem;
    }

    .score-pill {
        padding: 0.28rem 0.55rem;
        border-radius: 999px;
        color: #ffffff;
        font-weight: 800;
        font-size: 0.86rem;
        white-space: nowrap;
    }

    .green { background: var(--green); }
    .yellow { background: var(--yellow); }
    .red { background: var(--red); }

    .legend {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin: 0.35rem 0 0.75rem;
    }

    .legend-item {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        color: var(--muted);
        font-size: 0.84rem;
    }

    .dot {
        width: 0.72rem;
        height: 0.72rem;
        border-radius: 50%;
        display: inline-block;
    }

    .section-label {
        color: var(--muted);
        font-size: 0.82rem;
        font-weight: 700;
        margin: 0.3rem 0 0.6rem;
        text-transform: uppercase;
    }

    .note {
        border-left: 4px solid var(--blue);
        background: var(--note-bg);
        padding: 0.75rem 0.85rem;
        border-radius: 6px;
        margin: 0.55rem 0;
        color: var(--note-ink);
    }

    .warning {
        border-left: 4px solid var(--red);
        background: var(--warning-bg);
        padding: 0.75rem 0.85rem;
        border-radius: 6px;
        margin: 0.55rem 0;
        color: var(--warning-ink);
    }

    div[data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.75rem;
        box-shadow: var(--shadow);
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        color: var(--ink);
    }

    div[data-baseweb="input"],
    div[data-baseweb="textarea"],
    div[data-baseweb="select"] > div,
    textarea,
    input {
        background-color: var(--input-bg);
        color: var(--input-ink);
        border-color: var(--line);
    }

    div[data-baseweb="select"] span,
    div[data-baseweb="select"] div,
    div[data-baseweb="input"] input,
    div[data-baseweb="textarea"] textarea {
        color: var(--input-ink);
    }

    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: var(--surface);
        color: var(--ink);
        border-color: var(--line);
    }

    section[data-testid="stSidebar"] button,
    button[kind],
    div[data-testid="stTabs"] button {
        color: var(--ink);
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stTable"] {
        color: var(--ink);
    }

    @media (prefers-color-scheme: dark) {
        iframe,
        canvas {
            color-scheme: dark;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


LIGHT_THEME = {
    "scheme": "light",
    "paper": "#f7f5ef",
    "ink": "#20252b",
    "muted": "#6b7280",
    "line": "#e2ded3",
    "line_soft": "#ece8dd",
    "surface": "#ffffff",
    "surface_alt": "#fbfaf6",
    "chip_bg": "#f0ece2",
    "note_bg": "#f3f8fa",
    "note_ink": "#26323a",
    "warning_bg": "#fff5f3",
    "warning_ink": "#4b2f2d",
    "input_bg": "#ffffff",
    "input_ink": "#20252b",
    "green": "#239d72",
    "yellow": "#d9982f",
    "red": "#d95f5f",
    "blue": "#2f6f9f",
    "shadow": "0 1px 2px rgba(32, 37, 43, 0.05)",
}

DARK_THEME = {
    "scheme": "dark",
    "paper": "#0f1216",
    "ink": "#f0f3f6",
    "muted": "#a8b0ba",
    "line": "#2b3139",
    "line_soft": "#242a32",
    "surface": "#171b21",
    "surface_alt": "#1d232b",
    "chip_bg": "#252c35",
    "note_bg": "#142231",
    "note_ink": "#d7e7f5",
    "warning_bg": "#2a1a1d",
    "warning_ink": "#f5d1cf",
    "input_bg": "#11161c",
    "input_ink": "#f0f3f6",
    "green": "#3ecf98",
    "yellow": "#e7b75b",
    "red": "#ef7d7d",
    "blue": "#74aee8",
    "shadow": "0 1px 2px rgba(0, 0, 0, 0.38)",
}


def css_theme_variables(theme: dict[str, str]) -> str:
    return f"""
        color-scheme: {theme["scheme"]};
        --paper: {theme["paper"]};
        --ink: {theme["ink"]};
        --muted: {theme["muted"]};
        --line: {theme["line"]};
        --line-soft: {theme["line_soft"]};
        --surface: {theme["surface"]};
        --surface-alt: {theme["surface_alt"]};
        --chip-bg: {theme["chip_bg"]};
        --note-bg: {theme["note_bg"]};
        --note-ink: {theme["note_ink"]};
        --warning-bg: {theme["warning_bg"]};
        --warning-ink: {theme["warning_ink"]};
        --input-bg: {theme["input_bg"]};
        --input-ink: {theme["input_ink"]};
        --green: {theme["green"]};
        --yellow: {theme["yellow"]};
        --red: {theme["red"]};
        --blue: {theme["blue"]};
        --shadow: {theme["shadow"]};
        --background-color: {theme["paper"]};
        --secondary-background-color: {theme["surface"]};
        --text-color: {theme["ink"]};
        --primary-color: {theme["blue"]};
    """


def strong_theme_rules() -> str:
    return """
    html,
    body,
    .stApp,
    .main,
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stMain"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"] {
        background-color: var(--paper) !important;
        color: var(--ink) !important;
    }

    [data-testid="stHeader"] {
        background: color-mix(in srgb, var(--paper) 92%, transparent) !important;
    }

    [data-testid="stSidebar"],
    [data-testid="stSidebarContent"],
    section[data-testid="stSidebar"] > div {
        background-color: var(--surface) !important;
        color: var(--ink) !important;
        border-color: var(--line) !important;
    }

    .stApp *,
    [data-testid="stSidebar"] * {
        border-color: var(--line);
    }

    .stApp,
    .stApp p,
    .stApp span,
    .stApp label,
    .stApp li,
    .stApp div,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6,
    .stApp [data-testid="stMarkdownContainer"] {
        color: var(--ink);
    }

    .hero,
    .metric-card,
    .panel,
    div[data-testid="stMetric"],
    [data-testid="stExpander"],
    [data-testid="stDataFrame"],
    [data-testid="stTable"] {
        background-color: var(--surface) !important;
        color: var(--ink) !important;
        border-color: var(--line) !important;
    }

    .rank-row {
        border-bottom-color: var(--line-soft) !important;
    }

    .rank-num {
        background-color: var(--chip-bg) !important;
        color: var(--ink) !important;
    }

    .score-pill {
        color: #ffffff !important;
    }

    .score-pill.green,
    .dot.green {
        background-color: var(--green) !important;
    }

    .score-pill.yellow,
    .dot.yellow {
        background-color: var(--yellow) !important;
    }

    .score-pill.red,
    .dot.red {
        background-color: var(--red) !important;
    }

    .hero p,
    .rank-meta,
    .legend-item,
    .section-label,
    .metric-card small,
    .metric-card span,
    [data-testid="stCaptionContainer"],
    [data-testid="stMetricDelta"] {
        color: var(--muted) !important;
    }

    .note {
        background-color: var(--note-bg) !important;
        color: var(--note-ink) !important;
        border-left-color: var(--blue) !important;
    }

    .warning {
        background-color: var(--warning-bg) !important;
        color: var(--warning-ink) !important;
        border-left-color: var(--red) !important;
    }

    .note *,
    .warning * {
        color: inherit !important;
    }

    input,
    textarea,
    select,
    [data-baseweb="input"],
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"],
    [data-baseweb="textarea"] > div,
    [data-baseweb="select"],
    [data-baseweb="select"] > div,
    [data-baseweb="slider"] {
        background-color: var(--input-bg) !important;
        color: var(--input-ink) !important;
        border-color: var(--line) !important;
    }

    input::placeholder,
    textarea::placeholder,
    [data-baseweb="input"] input::placeholder,
    [data-baseweb="textarea"] textarea::placeholder {
        color: var(--muted) !important;
        opacity: 1 !important;
    }

    [data-baseweb="select"] *,
    [data-baseweb="input"] *,
    [data-baseweb="textarea"] *,
    [data-baseweb="checkbox"] *,
    [data-baseweb="radio"] * {
        color: var(--input-ink) !important;
    }

    [data-baseweb="popover"],
    [data-baseweb="menu"],
    [role="listbox"],
    [role="option"] {
        background-color: var(--surface) !important;
        color: var(--ink) !important;
        border-color: var(--line) !important;
    }

    [role="option"]:hover,
    [aria-selected="true"] {
        background-color: var(--surface-alt) !important;
        color: var(--ink) !important;
    }

    button,
    button[kind],
    [data-testid="stBaseButton-secondary"],
    [data-testid="stBaseButton-primary"],
    [data-testid="stTabs"] button {
        color: var(--ink) !important;
        border-color: var(--line) !important;
    }

    [data-testid="stBaseButton-secondary"],
    button[kind="secondary"] {
        background-color: var(--surface-alt) !important;
    }

    [data-testid="stTabs"] [role="tablist"] {
        border-bottom-color: var(--line) !important;
    }

    [data-testid="stAlert"] {
        background-color: var(--warning-bg) !important;
        color: var(--warning-ink) !important;
        border-color: var(--line) !important;
    }

    svg,
    svg * {
        color: inherit;
    }

    svg text {
        fill: var(--ink) !important;
    }

    .mini-chart {
        background-color: var(--surface) !important;
        border: 1px solid var(--line) !important;
        border-radius: 8px;
        box-shadow: var(--shadow);
        color: var(--ink) !important;
        padding: 0.8rem 0.9rem 0.65rem;
    }

    .mini-chart-plot {
        align-items: flex-end;
        background:
            repeating-linear-gradient(
                to top,
                transparent 0,
                transparent calc(25% - 1px),
                var(--line-soft) calc(25% - 1px),
                var(--line-soft) 25%
            );
        border-bottom: 1px solid var(--line);
        border-left: 1px solid var(--line);
        display: flex;
        gap: 0.7rem;
        height: var(--chart-height);
        padding: 1.65rem 0.55rem 0;
    }

    .mini-chart-col {
        align-items: stretch;
        display: flex;
        flex: 1 1 0;
        height: 100%;
        justify-content: flex-end;
        min-width: 0;
        position: relative;
    }

    .mini-chart-bar {
        background: var(--chart-bar, var(--blue));
        border-radius: 6px 6px 0 0;
        box-shadow: 0 0 0 1px color-mix(in srgb, #ffffff 16%, transparent) inset;
        height: var(--bar-height);
        min-height: 4px;
        width: 100%;
    }

    .mini-chart-value {
        bottom: calc(var(--bar-height) + 0.38rem);
        color: var(--ink) !important;
        font-size: 0.78rem;
        font-weight: 800;
        left: 50%;
        line-height: 1;
        position: absolute;
        transform: translateX(-50%);
        white-space: nowrap;
    }

    .mini-chart-labels {
        display: flex;
        gap: 0.7rem;
        margin-left: calc(1px + 0.55rem);
        margin-top: 0.55rem;
    }

    .mini-chart-label {
        color: var(--ink) !important;
        flex: 1 1 0;
        font-size: 0.78rem;
        font-weight: 700;
        line-height: 1.25;
        min-width: 0;
        overflow-wrap: anywhere;
        text-align: center;
    }

    .mini-chart-axis-title {
        color: var(--muted) !important;
        font-size: 0.75rem;
        font-weight: 700;
        margin-top: 0.45rem;
        text-align: center;
    }
    """


def theme_override_css(theme_mode: str) -> str:
    if theme_mode == "다크":
        body = f":root {{ {css_theme_variables(DARK_THEME)} }}\n{strong_theme_rules()}"
    elif theme_mode == "라이트":
        body = f":root {{ {css_theme_variables(LIGHT_THEME)} }}\n{strong_theme_rules()}"
    else:
        body = f"""
        @media (prefers-color-scheme: light) {{
            :root {{ {css_theme_variables(LIGHT_THEME)} }}
            {strong_theme_rules()}
        }}
        @media (prefers-color-scheme: dark) {{
            :root {{ {css_theme_variables(DARK_THEME)} }}
            {strong_theme_rules()}
        }}
        """
    return f"<style>{body}</style>"


BASE_WEIGHTS = {
    "rent_score": 0.28,
    "transport_score": 0.22,
    "safety_score": 0.18,
    "flood_score": 0.16,
    "convenience_score": 0.10,
    "night_safety_score": 0.06,
}

FLOOD_SCORE = {
    "낮음": 90,
    "보통": 64,
    "높음": 38,
}

ANCHOR_LOCATIONS = {
    "강남역": {
        "lat": 37.4979,
        "lon": 127.0276,
        "district": "강남구",
        "commute_column": "commute_gangnam",
        "aliases": ["강남역 11번 출구", "강남역11번출구"],
    },
    "홍대입구역": {
        "lat": 37.5572,
        "lon": 126.9245,
        "district": "마포구",
        "commute_column": "commute_hongdae",
        "aliases": ["홍대입구", "홍대"],
    },
    "종로": {
        "lat": 37.5704,
        "lon": 126.9831,
        "district": "종로구",
        "commute_column": "commute_jongno",
        "aliases": ["종각", "종각역", "종로3가"],
    },
    "여의도": {
        "lat": 37.5219,
        "lon": 126.9245,
        "district": "영등포구",
        "commute_column": "commute_yeouido",
        "aliases": ["여의도역", "국회의사당"],
    },
    "서울대입구": {
        "lat": 37.4812,
        "lon": 126.9527,
        "district": "관악구",
        "commute_column": "commute_snu",
        "aliases": ["서울대입구역", "샤로수길"],
    },
}

STATIC_SUBWAY_STATION_NAMES = sorted(
    {
        "4.19민주묘지역",
        "가락시장역",
        "가산디지털단지역",
        "가양역",
        "가오리역",
        "가좌역",
        "강남구청역",
        "강남역",
        "강동구청역",
        "강동역",
        "강변역",
        "강일역",
        "개롱역",
        "개봉역",
        "개포동역",
        "개화산역",
        "개화역",
        "거여역",
        "건대입구역",
        "경복궁역",
        "경찰병원역",
        "고덕역",
        "고려대역",
        "고속터미널역",
        "공덕역",
        "공릉역",
        "공항시장역",
        "광나루역",
        "광운대역",
        "광화문역",
        "광흥창역",
        "교대역",
        "구룡역",
        "구로디지털단지역",
        "구로역",
        "구반포역",
        "구산역",
        "구의역",
        "구일역",
        "구파발역",
        "국회의사당역",
        "군자역",
        "굽은다리역",
        "금천구청역",
        "금호역",
        "길동역",
        "길음역",
        "김포공항역",
        "까치산역",
        "낙성대역",
        "남구로역",
        "남부터미널역",
        "남성역",
        "남영역",
        "남태령역",
        "내방역",
        "녹번역",
        "녹사평역",
        "녹천역",
        "노들역",
        "노량진역",
        "노원역",
        "논현역",
        "당곡역",
        "당산역",
        "대림역",
        "대모산입구역",
        "대방역",
        "대청역",
        "대치역",
        "대흥역",
        "도곡역",
        "도림천역",
        "도봉산역",
        "도봉역",
        "독립문역",
        "독바위역",
        "독산역",
        "돌곶이역",
        "동대문역",
        "동대문역사문화공원역",
        "동대입구역",
        "동묘앞역",
        "동작역",
        "둔촌동역",
        "둔촌오륜역",
        "등촌역",
        "디지털미디어시티역",
        "뚝섬역",
        "뚝섬유원지역",
        "마곡나루역",
        "마곡역",
        "마들역",
        "마장역",
        "마천역",
        "마포구청역",
        "마포역",
        "망우역",
        "망원역",
        "매봉역",
        "먹골역",
        "면목역",
        "명동역",
        "명일역",
        "목동역",
        "몽촌토성역",
        "무악재역",
        "문래역",
        "문정역",
        "미아사거리역",
        "미아역",
        "반포역",
        "발산역",
        "방배역",
        "방이역",
        "방학역",
        "방화역",
        "버티고개역",
        "보라매공원역",
        "보라매병원역",
        "보라매역",
        "보문역",
        "복정역",
        "봉은사역",
        "봉천역",
        "봉화산역",
        "북한산보국문역",
        "북한산우이역",
        "불광역",
        "불암산역",
        "사가정역",
        "사당역",
        "사평역",
        "삼각지역",
        "삼성역",
        "삼성중앙역",
        "삼양사거리역",
        "삼양역",
        "삼전역",
        "상계역",
        "상도역",
        "상봉역",
        "상수역",
        "상왕십리역",
        "상월곡역",
        "상일동역",
        "새절역",
        "샛강역",
        "서강대역",
        "서대문역",
        "서빙고역",
        "서울대벤처타운역",
        "서울대입구역",
        "서울역",
        "서울숲역",
        "서울지방병무청역",
        "서원역",
        "서초역",
        "석계역",
        "석촌고분역",
        "석촌역",
        "선릉역",
        "선유도역",
        "선정릉역",
        "성신여대입구역",
        "성수역",
        "세종대왕기념관역",
        "솔밭공원역",
        "솔샘역",
        "송정역",
        "송파나루역",
        "송파역",
        "수락산역",
        "수서역",
        "수색역",
        "수유역",
        "숙대입구역",
        "숭실대입구역",
        "시청역",
        "신금호역",
        "신길역",
        "신내역",
        "신논현역",
        "신답역",
        "신당역",
        "신대방삼거리역",
        "신대방역",
        "신도림역",
        "신목동역",
        "신림역",
        "신반포역",
        "신방화역",
        "신사역",
        "신설동역",
        "신용산역",
        "신이문역",
        "신정네거리역",
        "신정역",
        "신촌역",
        "쌍문역",
        "아차산역",
        "아현역",
        "안국역",
        "안암역",
        "암사역",
        "압구정로데오역",
        "압구정역",
        "애오개역",
        "약수역",
        "양원역",
        "양재시민의숲역",
        "양재역",
        "양천구청역",
        "양천향교역",
        "양평역",
        "어린이대공원역",
        "언주역",
        "여의나루역",
        "여의도역",
        "역삼역",
        "역촌역",
        "연신내역",
        "염창역",
        "영등포구청역",
        "영등포시장역",
        "영등포역",
        "오금역",
        "오류동역",
        "오목교역",
        "옥수역",
        "온수역",
        "올림픽공원역",
        "왕십리역",
        "용답역",
        "용두역",
        "용마산역",
        "용산역",
        "우장산역",
        "월계역",
        "월곡역",
        "월드컵경기장역",
        "을지로3가역",
        "을지로4가역",
        "을지로입구역",
        "응봉역",
        "응암역",
        "이대역",
        "이수역",
        "이촌역",
        "일원역",
        "잠실나루역",
        "잠실새내역",
        "잠실역",
        "잠원역",
        "장승배기역",
        "장지역",
        "장한평역",
        "제기동역",
        "종각역",
        "종로3가역",
        "종로5가역",
        "종합운동장역",
        "중계역",
        "중곡역",
        "중랑역",
        "중앙보훈병원역",
        "증미역",
        "증산역",
        "창동역",
        "창신역",
        "청구역",
        "청계산입구역",
        "청담역",
        "청량리역",
        "총신대입구역",
        "충무로역",
        "충정로역",
        "태릉입구역",
        "한강진역",
        "한남역",
        "한성대입구역",
        "한양대역",
        "한티역",
        "합정역",
        "행당역",
        "혜화역",
        "홍대입구역",
        "홍제역",
        "화계역",
        "화곡역",
        "화랑대역",
        "회기역",
        "회현역",
        "효창공원앞역",
        "흑석역",
    }
)

DISTRICT_CENTERS = {
    "강남구": {"lat": 37.5172, "lon": 127.0473, "aliases": ["강남구청", "삼성동", "역삼동"]},
    "강동구": {"lat": 37.5301, "lon": 127.1238, "aliases": ["강동구청", "천호동", "천호"]},
    "강북구": {"lat": 37.6396, "lon": 127.0257, "aliases": ["강북구청", "수유동", "미아동"]},
    "강서구": {"lat": 37.5509, "lon": 126.8495, "aliases": ["강서구청", "화곡동", "마곡"]},
    "관악구": {"lat": 37.4784, "lon": 126.9516, "aliases": ["관악구청", "신림동", "봉천동"]},
    "광진구": {"lat": 37.5385, "lon": 127.0823, "aliases": ["광진구청", "건대입구", "자양동"]},
    "구로구": {"lat": 37.4955, "lon": 126.8877, "aliases": ["구로구청", "구로동", "구디"]},
    "금천구": {"lat": 37.4569, "lon": 126.8955, "aliases": ["금천구청", "독산동", "가산디지털단지"]},
    "노원구": {"lat": 37.6542, "lon": 127.0568, "aliases": ["노원구청", "노원역", "상계동"]},
    "도봉구": {"lat": 37.6688, "lon": 127.0471, "aliases": ["도봉구청", "창동", "쌍문동"]},
    "동대문구": {"lat": 37.5744, "lon": 127.0396, "aliases": ["동대문구청", "회기동", "청량리"]},
    "동작구": {"lat": 37.5124, "lon": 126.9393, "aliases": ["동작구청", "노량진", "노량진동"]},
    "마포구": {"lat": 37.5663, "lon": 126.9019, "aliases": ["마포구청", "연남동", "망원동"]},
    "서대문구": {"lat": 37.5791, "lon": 126.9368, "aliases": ["서대문구청", "홍제동", "신촌"]},
    "서초구": {"lat": 37.4837, "lon": 127.0324, "aliases": ["서초구청", "방배동", "교대역"]},
    "성동구": {"lat": 37.5633, "lon": 127.0369, "aliases": ["성동구청", "성수동", "왕십리"]},
    "성북구": {"lat": 37.5894, "lon": 127.0167, "aliases": ["성북구청", "안암동", "성신여대"]},
    "송파구": {"lat": 37.5145, "lon": 127.1059, "aliases": ["송파구청", "잠실동", "잠실"]},
    "양천구": {"lat": 37.5170, "lon": 126.8665, "aliases": ["양천구청", "목동", "오목교"]},
    "영등포구": {"lat": 37.5264, "lon": 126.8962, "aliases": ["영등포구청", "영등포", "문래동"]},
    "용산구": {"lat": 37.5326, "lon": 126.9900, "aliases": ["용산구청", "이태원", "효창동"]},
    "은평구": {"lat": 37.6027, "lon": 126.9291, "aliases": ["은평구청", "불광동", "연신내"]},
    "종로구": {"lat": 37.5735, "lon": 126.9788, "aliases": ["종로구청", "광화문", "혜화동"]},
    "중구": {"lat": 37.5636, "lon": 126.9976, "aliases": ["중구청", "명동", "을지로", "충무로"]},
    "중랑구": {"lat": 37.6063, "lon": 127.0926, "aliases": ["중랑구청", "상봉동", "면목동"]},
}

LANDMARK_LOCATIONS = {
    "서울시청": {"lat": 37.5663, "lon": 126.9779, "district": "중구", "aliases": ["시청", "시청역", "덕수궁"]},
    "을지로입구역": {"lat": 37.5660, "lon": 126.9827, "district": "중구", "aliases": ["을지로입구", "을지로"]},
    "명동역": {"lat": 37.5609, "lon": 126.9864, "district": "중구", "aliases": ["명동"]},
    "충무로역": {"lat": 37.5612, "lon": 126.9942, "district": "중구", "aliases": ["충무로"]},
    "동대문역사문화공원역": {
        "lat": 37.5657,
        "lon": 127.0095,
        "district": "중구",
        "aliases": ["동대문역사문화공원", "ddp", "동대문디자인플라자"],
    },
    "광화문역": {"lat": 37.5716, "lon": 126.9769, "district": "종로구", "aliases": ["광화문", "세종문화회관"]},
    "종각역": {"lat": 37.5702, "lon": 126.9829, "district": "종로구", "aliases": ["종각"]},
    "가산디지털단지역": {"lat": 37.4816, "lon": 126.8826, "district": "금천구", "aliases": ["가산디지털단지", "가디"]},
    "마곡나루역": {"lat": 37.5668, "lon": 126.8270, "district": "강서구", "aliases": ["마곡나루", "마곡"]},
    "잠실역": {"lat": 37.5133, "lon": 127.1002, "district": "송파구", "aliases": ["잠실"]},
}

SEOUL_BOUNDS = {
    "min_lat": 37.41,
    "max_lat": 37.72,
    "min_lon": 126.73,
    "max_lon": 127.20,
}


def square_polygon(lat: float, lon: float, size: float = 0.0075) -> list[list[float]]:
    return [
        [lon - size, lat - size * 0.72],
        [lon + size, lat - size * 0.72],
        [lon + size, lat + size * 0.72],
        [lon - size, lat + size * 0.72],
    ]


def normalize_place_text(value: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]", "", value.lower())


def is_in_seoul(lat: float, lon: float) -> bool:
    return (
        SEOUL_BOUNDS["min_lat"] <= lat <= SEOUL_BOUNDS["max_lat"]
        and SEOUL_BOUNDS["min_lon"] <= lon <= SEOUL_BOUNDS["max_lon"]
    )


def station_display_name(name: str) -> str:
    cleaned = re.sub(r"\s*\([^)]*\)", "", name).strip()
    cleaned = cleaned.replace("驛", "역")
    if not cleaned:
        return cleaned
    return cleaned if cleaned.endswith("역") else f"{cleaned}역"


def station_sort_key(name: str) -> str:
    return normalize_place_text(name.removesuffix("역"))


def location_from_seed(name: str, location: dict[str, object], source: str) -> dict[str, object]:
    return {
        "name": station_display_name(name),
        "district": location.get("district", "서울"),
        "lat": float(location["lat"]),
        "lon": float(location["lon"]),
        "source": source,
        "matched_text": name,
        "commute_column": location.get("commute_column"),
    }


def seeded_subway_stations() -> dict[str, dict[str, object]]:
    stations: dict[str, dict[str, object]] = {
        station_name: {
            "name": station_name,
            "district": "서울",
            "source": "내장 역명 목록",
            "matched_text": station_name,
        }
        for station_name in STATIC_SUBWAY_STATION_NAMES
    }

    for name, location in ANCHOR_LOCATIONS.items():
        stations[station_display_name(name)] = location_from_seed(name, location, "내장 기준지")

    for name, location in LANDMARK_LOCATIONS.items():
        if name.endswith("역"):
            stations[station_display_name(name)] = location_from_seed(name, location, "내장 주요 역")

    return stations


def overpass_station_query() -> str:
    return """
    [out:json][timeout:25];
    area["name:ko"="서울특별시"]["boundary"="administrative"]->.seoul;
    (
      node["railway"="station"](area.seoul);
      node["railway"="halt"](area.seoul);
      node["public_transport"="station"]["subway"="yes"](area.seoul);
    );
    out body;
    """


def looks_like_subway_station(tags: dict[str, str]) -> bool:
    station_tag = tags.get("station", "")
    railway = tags.get("railway", "")
    subway = tags.get("subway", "")
    network = tags.get("network", "")
    operator = tags.get("operator", "")
    route_ref = tags.get("ref", "")
    combined = " ".join([station_tag, railway, subway, network, operator, route_ref]).lower()
    return (
        subway == "yes"
        or station_tag in {"subway", "light_rail", "train"}
        or "seoul" in combined
        or "metro" in combined
        or "서울" in combined
        or "수도권" in combined
    )


@st.cache_data(ttl=60 * 60 * 24 * 7, show_spinner=False)
def fetch_overpass_subway_stations() -> dict[str, dict[str, object]]:
    params = urllib.parse.urlencode({"data": overpass_station_query()}).encode("utf-8")
    urls = [
        "https://overpass-api.de/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter",
    ]

    for url in urls:
        request = urllib.request.Request(
            url,
            data=params,
            headers={
                "User-Agent": "pgis-monthly-rent-survival-map/1.0",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            continue

        stations: dict[str, dict[str, object]] = {}
        for element in payload.get("elements", []):
            tags = element.get("tags", {})
            raw_name = tags.get("name:ko") or tags.get("name")
            if not raw_name or not looks_like_subway_station(tags):
                continue

            lat = element.get("lat")
            lon = element.get("lon")
            if lat is None or lon is None:
                continue

            lat = float(lat)
            lon = float(lon)
            if not is_in_seoul(lat, lon):
                continue

            name = station_display_name(raw_name)
            if not name or not re.search(r"[가-힣]", name):
                continue

            stations[name] = {
                "name": name,
                "district": "서울",
                "lat": lat,
                "lon": lon,
                "source": "OSM 지하철역 목록",
                "matched_text": raw_name,
            }

        if stations:
            return stations

    return {}


def load_subway_stations() -> dict[str, dict[str, object]]:
    stations = seeded_subway_stations()
    stations.update(fetch_overpass_subway_stations())
    return dict(sorted(stations.items(), key=lambda item: station_sort_key(item[0])))


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_km = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def target_basis_label(target_location: dict[str, object] | None, fallback_label: str) -> str:
    if target_location is None:
        return f"{fallback_label} 기준"
    district = target_location.get("district")
    name = target_location.get("name")
    return f"{name} 기준" if not district else f"{name}({district}) 기준"


def local_geocode_candidates(
    df: pd.DataFrame,
    subway_stations: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []

    for name, location in ANCHOR_LOCATIONS.items():
        names = [name, *location["aliases"]]
        candidates.append(
            {
                "name": name,
                "district": location["district"],
                "lat": location["lat"],
                "lon": location["lon"],
                "source": "기준지",
                "commute_column": location["commute_column"],
                "match_terms": names,
                "priority": 50,
            }
        )

    for name, location in LANDMARK_LOCATIONS.items():
        names = [name, *location["aliases"]]
        candidates.append(
            {
                "name": name,
                "district": location["district"],
                "lat": location["lat"],
                "lon": location["lon"],
                "source": "주요 지점",
                "match_terms": names,
                "priority": 45,
            }
        )

    for name, location in subway_stations.items():
        names = [name, name.removesuffix("역")]
        if location.get("matched_text"):
            names.append(str(location["matched_text"]))
        candidate = {
            "name": name,
            "district": location.get("district", "서울"),
            "source": location.get("source", "지하철역 목록"),
            "matched_text": name,
            "match_terms": names,
            "priority": 48,
            "kind": "subway_station",
        }
        if location.get("lat") is not None and location.get("lon") is not None:
            candidate["lat"] = float(location["lat"])
            candidate["lon"] = float(location["lon"])
        if location.get("commute_column"):
            candidate["commute_column"] = location["commute_column"]
        candidates.append(candidate)

    for district, location in DISTRICT_CENTERS.items():
        names = [district, *location["aliases"]]
        candidates.append(
            {
                "name": district,
                "district": district,
                "lat": location["lat"],
                "lon": location["lon"],
                "source": "서울 구 중심",
                "match_terms": names,
                "priority": 35,
            }
        )

    for row in df.itertuples():
        names = [row.dong, f"{row.district}{row.dong}"]
        candidates.append(
            {
                "name": row.dong,
                "district": row.district,
                "lat": float(row.lat),
                "lon": float(row.lon),
                "source": "동네 데이터",
                "match_terms": names,
                "priority": 40,
            }
        )

    return candidates


def geocode_from_local_index(
    address: str,
    df: pd.DataFrame,
    subway_stations: dict[str, dict[str, object]],
) -> dict[str, object] | None:
    query = normalize_place_text(address)
    if not query:
        return None

    best_match: dict[str, object] | None = None
    best_score = 0

    for candidate in local_geocode_candidates(df, subway_stations):
        for term in candidate["match_terms"]:
            normalized_term = normalize_place_text(str(term))
            if len(normalized_term) < 2:
                continue

            score = 0
            if normalized_term in query:
                score = len(normalized_term) * 10 + int(candidate["priority"])
            elif len(query) >= 3 and query in normalized_term:
                score = len(query) * 8 + int(candidate["priority"])

            if score > best_score:
                best_score = score
                best_match = {
                    **candidate,
                    "matched_text": term,
                }

    if best_match is None:
        return None

    best_match.pop("match_terms", None)
    best_match.pop("priority", None)

    if best_match.get("kind") == "subway_station" and (
        best_match.get("lat") is None or best_match.get("lon") is None
    ):
        resolved = resolve_subway_station_location(str(best_match["name"]), subway_stations)
        if resolved is None:
            return None
        best_match.update(resolved)

    best_match.pop("kind", None)
    return best_match


@st.cache_data(ttl=60 * 60 * 24, show_spinner=False)
def geocode_from_osm(address: str) -> dict[str, object] | None:
    query = address if "서울" in address else f"{address}, 서울, 대한민국"
    params = urllib.parse.urlencode(
        {
            "q": query,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }
    )
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "pgis-monthly-rent-survival-map/1.0",
            "Accept": "application/json",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=3) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    if not payload:
        return None

    result = payload[0]
    lat = float(result["lat"])
    lon = float(result["lon"])
    if not is_in_seoul(lat, lon):
        return None

    address_detail = result.get("address", {})
    district = (
        address_detail.get("city_district")
        or address_detail.get("borough")
        or address_detail.get("suburb")
        or "서울"
    )
    display_name = result.get("display_name", address).split(",")[0]
    return {
        "name": display_name,
        "district": district,
        "lat": lat,
        "lon": lon,
        "source": "외부 지오코딩",
        "matched_text": address,
    }


def resolve_subway_station_location(
    station_name: str,
    subway_stations: dict[str, dict[str, object]],
) -> dict[str, object] | None:
    normalized = station_display_name(station_name)
    station = subway_stations.get(normalized)
    if station and station.get("lat") is not None and station.get("lon") is not None:
        return {
            **station,
            "name": normalized,
            "lat": float(station["lat"]),
            "lon": float(station["lon"]),
            "matched_text": station.get("matched_text", normalized),
        }

    geocoded = geocode_from_osm(normalized)
    if geocoded is None:
        return None

    return {
        **geocoded,
        "name": normalized,
        "source": "역명 지오코딩",
        "matched_text": normalized,
    }


def geocode_target(
    address: str,
    df: pd.DataFrame,
    subway_stations: dict[str, dict[str, object]],
) -> dict[str, object] | None:
    stripped = address.strip()
    if not stripped:
        return None

    local_match = geocode_from_local_index(stripped, df, subway_stations)
    if local_match is not None:
        return local_match

    if len(normalize_place_text(stripped)) < 4:
        return None

    return geocode_from_osm(stripped)


def estimate_commute_minutes(row: pd.Series, target_location: dict[str, object]) -> int:
    distance_km = haversine_km(
        float(row["lat"]),
        float(row["lon"]),
        float(target_location["lat"]),
        float(target_location["lon"]),
    )
    transfer_penalty = 0 if distance_km < 2 else 3 if distance_km < 7 else 5
    estimated = float(row["station_walk"]) + 9 + distance_km * 2.6 + transfer_penalty
    return int(round(max(8, estimated)))


@st.cache_data
def load_neighborhoods() -> pd.DataFrame:
    rows = [
        {
            "dong": "역삼동",
            "district": "강남구",
            "lat": 37.5007,
            "lon": 127.0364,
            "deposit": 3000,
            "monthly_rent": 86,
            "station_walk": 6,
            "bus_stops": 18,
            "safety_score": 79,
            "night_safety_score": 74,
            "flood_risk": "낮음",
            "flood_history": "주요 업무지구 중심부 침수 리스크 낮음",
            "facilities": 93,
            "semi_basement_share": 6,
            "cctv_density": 86,
            "streetlight_density": 84,
            "one_room": 86,
            "officetel": 118,
            "villa": 90,
            "commute_gangnam": 7,
            "commute_hongdae": 38,
            "commute_jongno": 35,
            "commute_yeouido": 32,
            "commute_snu": 31,
            "caution": "월세와 관리비 부담이 커서 실거주 비용을 함께 확인",
            "reviews": ["강남 업무지구 접근성은 최상", "저렴한 매물은 면적과 채광 차이가 큼"],
        },
        {
            "dong": "천호동",
            "district": "강동구",
            "lat": 37.5385,
            "lon": 127.1238,
            "deposit": 2000,
            "monthly_rent": 60,
            "station_walk": 7,
            "bus_stops": 15,
            "safety_score": 70,
            "night_safety_score": 66,
            "flood_risk": "보통",
            "flood_history": "한강 인접 저지대와 배수 상태 확인",
            "facilities": 82,
            "semi_basement_share": 12,
            "cctv_density": 72,
            "streetlight_density": 76,
            "one_room": 60,
            "officetel": 78,
            "villa": 63,
            "commute_gangnam": 31,
            "commute_hongdae": 55,
            "commute_jongno": 40,
            "commute_yeouido": 52,
            "commute_snu": 57,
            "caution": "상권 주변은 밤 소음과 주차 여건을 확인",
            "reviews": ["생활 편의시설이 고르게 있음", "강남 동쪽 출퇴근이면 선택지가 넓음"],
        },
        {
            "dong": "미아동",
            "district": "강북구",
            "lat": 37.6264,
            "lon": 127.0263,
            "deposit": 1000,
            "monthly_rent": 43,
            "station_walk": 8,
            "bus_stops": 13,
            "safety_score": 64,
            "night_safety_score": 60,
            "flood_risk": "낮음",
            "flood_history": "대체로 낮음",
            "facilities": 76,
            "semi_basement_share": 16,
            "cctv_density": 68,
            "streetlight_density": 70,
            "one_room": 43,
            "officetel": 58,
            "villa": 46,
            "commute_gangnam": 52,
            "commute_hongdae": 47,
            "commute_jongno": 31,
            "commute_yeouido": 55,
            "commute_snu": 67,
            "caution": "언덕 매물과 늦은 귀가 동선을 실제로 확인",
            "reviews": ["월세 선택지가 비교적 넓음", "도심 통근은 환승 동선이 중요"],
        },
        {
            "dong": "화곡동",
            "district": "강서구",
            "lat": 37.5412,
            "lon": 126.8405,
            "deposit": 1000,
            "monthly_rent": 50,
            "station_walk": 8,
            "bus_stops": 15,
            "safety_score": 58,
            "night_safety_score": 57,
            "flood_risk": "보통",
            "flood_history": "집중호우 시 배수 취약 구간",
            "facilities": 76,
            "semi_basement_share": 18,
            "cctv_density": 64,
            "streetlight_density": 68,
            "one_room": 50,
            "officetel": 66,
            "villa": 53,
            "commute_gangnam": 50,
            "commute_hongdae": 32,
            "commute_jongno": 42,
            "commute_yeouido": 28,
            "commute_snu": 49,
            "caution": "월세 대비 교통은 좋지만 범죄·소음·주차를 확인",
            "reviews": ["큰길 근처와 안쪽 골목 체감 차이 있음", "매물 수는 많은 편"],
        },
        {
            "dong": "신림동",
            "district": "관악구",
            "lat": 37.4843,
            "lon": 126.9295,
            "deposit": 1000,
            "monthly_rent": 48,
            "station_walk": 7,
            "bus_stops": 14,
            "safety_score": 62,
            "night_safety_score": 58,
            "flood_risk": "보통",
            "flood_history": "저지대 일부 침수 이력",
            "facilities": 82,
            "semi_basement_share": 21,
            "cctv_density": 68,
            "streetlight_density": 72,
            "one_room": 48,
            "officetel": 64,
            "villa": 52,
            "commute_gangnam": 32,
            "commute_hongdae": 38,
            "commute_jongno": 45,
            "commute_yeouido": 34,
            "commute_snu": 8,
            "caution": "월세는 낮지만 침수와 야간 골목길 리스크를 함께 확인",
            "reviews": ["역 주변 생활시설은 충분", "언덕과 골목 동선 차이가 큼"],
        },
        {
            "dong": "자양동",
            "district": "광진구",
            "lat": 37.5319,
            "lon": 127.0833,
            "deposit": 2000,
            "monthly_rent": 63,
            "station_walk": 11,
            "bus_stops": 10,
            "safety_score": 73,
            "night_safety_score": 70,
            "flood_risk": "보통",
            "flood_history": "한강 인접 구간 배수 확인",
            "facilities": 84,
            "semi_basement_share": 12,
            "cctv_density": 76,
            "streetlight_density": 79,
            "one_room": 63,
            "officetel": 81,
            "villa": 66,
            "commute_gangnam": 24,
            "commute_hongdae": 38,
            "commute_jongno": 34,
            "commute_yeouido": 42,
            "commute_snu": 53,
            "caution": "역 도보 시간이 길어지는 매물은 버스 동선 확인",
            "reviews": ["강남 접근성이 좋음", "마트와 생활시설 균형이 좋음"],
        },
        {
            "dong": "구로동",
            "district": "구로구",
            "lat": 37.4955,
            "lon": 126.8877,
            "deposit": 1000,
            "monthly_rent": 45,
            "station_walk": 8,
            "bus_stops": 16,
            "safety_score": 62,
            "night_safety_score": 59,
            "flood_risk": "보통",
            "flood_history": "저지대와 하천 인접 구간 점검",
            "facilities": 80,
            "semi_basement_share": 18,
            "cctv_density": 67,
            "streetlight_density": 70,
            "one_room": 45,
            "officetel": 62,
            "villa": 49,
            "commute_gangnam": 43,
            "commute_hongdae": 34,
            "commute_jongno": 42,
            "commute_yeouido": 24,
            "commute_snu": 38,
            "caution": "산업단지 인접 매물은 소음과 야간 동선을 확인",
            "reviews": ["월세 대비 교통 선택지가 많음", "업무지구와 주거지 체감 차이가 큼"],
        },
        {
            "dong": "독산동",
            "district": "금천구",
            "lat": 37.4692,
            "lon": 126.8970,
            "deposit": 1000,
            "monthly_rent": 42,
            "station_walk": 11,
            "bus_stops": 12,
            "safety_score": 60,
            "night_safety_score": 56,
            "flood_risk": "보통",
            "flood_history": "저지대와 하천 인접 구간 점검",
            "facilities": 70,
            "semi_basement_share": 19,
            "cctv_density": 63,
            "streetlight_density": 66,
            "one_room": 42,
            "officetel": 58,
            "villa": 46,
            "commute_gangnam": 52,
            "commute_hongdae": 48,
            "commute_jongno": 50,
            "commute_yeouido": 32,
            "commute_snu": 40,
            "caution": "예산은 좋지만 야간안전과 역 접근성을 확인",
            "reviews": ["월세 선택지가 넓음", "생활권이 역에서 멀어질 수 있음"],
        },
        {
            "dong": "상계동",
            "district": "노원구",
            "lat": 37.6543,
            "lon": 127.0568,
            "deposit": 1000,
            "monthly_rent": 43,
            "station_walk": 7,
            "bus_stops": 15,
            "safety_score": 68,
            "night_safety_score": 65,
            "flood_risk": "낮음",
            "flood_history": "대체로 낮음",
            "facilities": 82,
            "semi_basement_share": 13,
            "cctv_density": 71,
            "streetlight_density": 76,
            "one_room": 43,
            "officetel": 60,
            "villa": 48,
            "commute_gangnam": 60,
            "commute_hongdae": 58,
            "commute_jongno": 38,
            "commute_yeouido": 65,
            "commute_snu": 76,
            "caution": "도심·강남 통근이면 이동 시간이 길 수 있음",
            "reviews": ["생활 인프라는 안정적", "예산 대비 면적 선택지가 있음"],
        },
        {
            "dong": "창동",
            "district": "도봉구",
            "lat": 37.6532,
            "lon": 127.0477,
            "deposit": 1000,
            "monthly_rent": 42,
            "station_walk": 6,
            "bus_stops": 14,
            "safety_score": 69,
            "night_safety_score": 66,
            "flood_risk": "낮음",
            "flood_history": "대체로 낮음",
            "facilities": 79,
            "semi_basement_share": 12,
            "cctv_density": 70,
            "streetlight_density": 75,
            "one_room": 42,
            "officetel": 58,
            "villa": 47,
            "commute_gangnam": 58,
            "commute_hongdae": 56,
            "commute_jongno": 36,
            "commute_yeouido": 63,
            "commute_snu": 74,
            "caution": "목적지에 따라 환승 피로도가 커질 수 있음",
            "reviews": ["역세권은 생활 편의가 좋음", "조용한 주거지를 찾기 좋음"],
        },
        {
            "dong": "회기동",
            "district": "동대문구",
            "lat": 37.5908,
            "lon": 127.0571,
            "deposit": 1000,
            "monthly_rent": 47,
            "station_walk": 7,
            "bus_stops": 12,
            "safety_score": 69,
            "night_safety_score": 66,
            "flood_risk": "낮음",
            "flood_history": "대체로 낮음",
            "facilities": 80,
            "semi_basement_share": 14,
            "cctv_density": 70,
            "streetlight_density": 75,
            "one_room": 47,
            "officetel": 62,
            "villa": 51,
            "commute_gangnam": 43,
            "commute_hongdae": 41,
            "commute_jongno": 28,
            "commute_yeouido": 48,
            "commute_snu": 60,
            "caution": "대학가 원룸은 방음과 관리 상태를 확인",
            "reviews": ["식비와 생활비를 낮추기 좋음", "학기 중 유동인구가 많음"],
        },
        {
            "dong": "노량진동",
            "district": "동작구",
            "lat": 37.5136,
            "lon": 126.9422,
            "deposit": 1000,
            "monthly_rent": 46,
            "station_walk": 7,
            "bus_stops": 15,
            "safety_score": 61,
            "night_safety_score": 59,
            "flood_risk": "보통",
            "flood_history": "저지대 일부 배수 점검",
            "facilities": 83,
            "semi_basement_share": 20,
            "cctv_density": 66,
            "streetlight_density": 69,
            "one_room": 46,
            "officetel": 61,
            "villa": 50,
            "commute_gangnam": 34,
            "commute_hongdae": 31,
            "commute_jongno": 29,
            "commute_yeouido": 17,
            "commute_snu": 30,
            "caution": "저렴한 매물은 채광·방음·반지하 여부 확인",
            "reviews": ["식당과 편의시설이 많음", "고시원 밀집 구간은 소음 확인"],
        },
        {
            "dong": "망원동",
            "district": "마포구",
            "lat": 37.5568,
            "lon": 126.9100,
            "deposit": 1500,
            "monthly_rent": 62,
            "station_walk": 9,
            "bus_stops": 13,
            "safety_score": 72,
            "night_safety_score": 68,
            "flood_risk": "보통",
            "flood_history": "한강 인접 저지대 점검 필요",
            "facilities": 88,
            "semi_basement_share": 13,
            "cctv_density": 75,
            "streetlight_density": 78,
            "one_room": 62,
            "officetel": 80,
            "villa": 66,
            "commute_gangnam": 45,
            "commute_hongdae": 14,
            "commute_jongno": 34,
            "commute_yeouido": 29,
            "commute_snu": 49,
            "caution": "상권 인접 매물은 소음과 주차 여건을 확인",
            "reviews": ["시장과 마트 접근성이 좋음", "매물별 채광 차이가 큼"],
        },
        {
            "dong": "홍제동",
            "district": "서대문구",
            "lat": 37.5899,
            "lon": 126.9448,
            "deposit": 1500,
            "monthly_rent": 49,
            "station_walk": 8,
            "bus_stops": 11,
            "safety_score": 71,
            "night_safety_score": 68,
            "flood_risk": "낮음",
            "flood_history": "침수 리스크 낮음",
            "facilities": 74,
            "semi_basement_share": 12,
            "cctv_density": 74,
            "streetlight_density": 76,
            "one_room": 49,
            "officetel": 65,
            "villa": 52,
            "commute_gangnam": 42,
            "commute_hongdae": 31,
            "commute_jongno": 21,
            "commute_yeouido": 43,
            "commute_snu": 58,
            "caution": "언덕과 버스 환승 동선을 실제로 확인",
            "reviews": ["종로 접근성이 좋음", "조용한 주거지 선호자에게 적합"],
        },
        {
            "dong": "방배동",
            "district": "서초구",
            "lat": 37.4816,
            "lon": 126.9977,
            "deposit": 3000,
            "monthly_rent": 80,
            "station_walk": 8,
            "bus_stops": 13,
            "safety_score": 78,
            "night_safety_score": 74,
            "flood_risk": "낮음",
            "flood_history": "주요 주거지 침수 리스크 낮음",
            "facilities": 84,
            "semi_basement_share": 7,
            "cctv_density": 80,
            "streetlight_density": 82,
            "one_room": 80,
            "officetel": 100,
            "villa": 82,
            "commute_gangnam": 18,
            "commute_hongdae": 42,
            "commute_jongno": 37,
            "commute_yeouido": 34,
            "commute_snu": 22,
            "caution": "조용한 주거지는 좋지만 예산 상한을 넉넉히 잡아야 함",
            "reviews": ["강남·관악 접근성 균형이 좋음", "빌라 매물 관리 상태 확인 필요"],
        },
        {
            "dong": "왕십리",
            "district": "성동구",
            "lat": 37.5614,
            "lon": 127.0375,
            "deposit": 2000,
            "monthly_rent": 65,
            "station_walk": 6,
            "bus_stops": 16,
            "safety_score": 78,
            "night_safety_score": 75,
            "flood_risk": "낮음",
            "flood_history": "반복 침수 위험 낮음",
            "facilities": 89,
            "semi_basement_share": 10,
            "cctv_density": 84,
            "streetlight_density": 83,
            "one_room": 65,
            "officetel": 82,
            "villa": 68,
            "commute_gangnam": 27,
            "commute_hongdae": 28,
            "commute_jongno": 23,
            "commute_yeouido": 33,
            "commute_snu": 42,
            "caution": "역세권 매물은 관리비와 소음 차이가 큼",
            "reviews": ["환승 접근성이 매우 좋음", "대학가와 상권이 가까움"],
        },
        {
            "dong": "안암동",
            "district": "성북구",
            "lat": 37.5867,
            "lon": 127.0217,
            "deposit": 1000,
            "monthly_rent": 48,
            "station_walk": 7,
            "bus_stops": 13,
            "safety_score": 70,
            "night_safety_score": 66,
            "flood_risk": "낮음",
            "flood_history": "대체로 낮음",
            "facilities": 83,
            "semi_basement_share": 14,
            "cctv_density": 72,
            "streetlight_density": 75,
            "one_room": 48,
            "officetel": 64,
            "villa": 52,
            "commute_gangnam": 43,
            "commute_hongdae": 40,
            "commute_jongno": 22,
            "commute_yeouido": 48,
            "commute_snu": 59,
            "caution": "대학가 인접 매물은 학기 중 소음을 확인",
            "reviews": ["도심 접근성과 월세 균형이 좋음", "원룸 선택지가 다양함"],
        },
        {
            "dong": "잠실동",
            "district": "송파구",
            "lat": 37.5133,
            "lon": 127.1002,
            "deposit": 3000,
            "monthly_rent": 78,
            "station_walk": 7,
            "bus_stops": 16,
            "safety_score": 80,
            "night_safety_score": 76,
            "flood_risk": "보통",
            "flood_history": "한강·탄천 인접 구간 배수 확인",
            "facilities": 90,
            "semi_basement_share": 7,
            "cctv_density": 84,
            "streetlight_density": 85,
            "one_room": 78,
            "officetel": 102,
            "villa": 80,
            "commute_gangnam": 20,
            "commute_hongdae": 45,
            "commute_jongno": 37,
            "commute_yeouido": 40,
            "commute_snu": 44,
            "caution": "상업지 인접 매물은 소음과 월세 상승폭 확인",
            "reviews": ["생활 편의와 안전 체감이 좋음", "예산 부담은 큰 편"],
        },
        {
            "dong": "목동",
            "district": "양천구",
            "lat": 37.5267,
            "lon": 126.8646,
            "deposit": 2000,
            "monthly_rent": 62,
            "station_walk": 9,
            "bus_stops": 14,
            "safety_score": 76,
            "night_safety_score": 72,
            "flood_risk": "보통",
            "flood_history": "안양천 인접 구간 배수 확인",
            "facilities": 87,
            "semi_basement_share": 10,
            "cctv_density": 79,
            "streetlight_density": 81,
            "one_room": 62,
            "officetel": 78,
            "villa": 65,
            "commute_gangnam": 43,
            "commute_hongdae": 28,
            "commute_jongno": 39,
            "commute_yeouido": 23,
            "commute_snu": 47,
            "caution": "목적지에 따라 지하철 환승 또는 버스 의존도가 달라짐",
            "reviews": ["생활권이 안정적", "조용한 주거지를 찾기 좋음"],
        },
        {
            "dong": "영등포동",
            "district": "영등포구",
            "lat": 37.5206,
            "lon": 126.9056,
            "deposit": 1500,
            "monthly_rent": 55,
            "station_walk": 6,
            "bus_stops": 18,
            "safety_score": 65,
            "night_safety_score": 61,
            "flood_risk": "보통",
            "flood_history": "저지대 일부 배수 점검",
            "facilities": 90,
            "semi_basement_share": 15,
            "cctv_density": 74,
            "streetlight_density": 76,
            "one_room": 55,
            "officetel": 72,
            "villa": 58,
            "commute_gangnam": 36,
            "commute_hongdae": 25,
            "commute_jongno": 28,
            "commute_yeouido": 10,
            "commute_snu": 35,
            "caution": "유흥가 인접 매물은 야간 소음과 귀가길 확인",
            "reviews": ["여의도 접근성이 매우 좋음", "상권과 주거지 분위기 차이가 큼"],
        },
        {
            "dong": "효창동",
            "district": "용산구",
            "lat": 37.5424,
            "lon": 126.9618,
            "deposit": 2000,
            "monthly_rent": 67,
            "station_walk": 8,
            "bus_stops": 14,
            "safety_score": 74,
            "night_safety_score": 70,
            "flood_risk": "낮음",
            "flood_history": "대체로 낮음",
            "facilities": 85,
            "semi_basement_share": 10,
            "cctv_density": 78,
            "streetlight_density": 80,
            "one_room": 67,
            "officetel": 86,
            "villa": 70,
            "commute_gangnam": 30,
            "commute_hongdae": 24,
            "commute_jongno": 18,
            "commute_yeouido": 20,
            "commute_snu": 39,
            "caution": "언덕과 골목 동선이 매물별로 크게 다름",
            "reviews": ["도심과 여의도 접근성이 좋음", "조용한 주거지를 찾기 좋음"],
        },
        {
            "dong": "불광동",
            "district": "은평구",
            "lat": 37.6100,
            "lon": 126.9293,
            "deposit": 1000,
            "monthly_rent": 45,
            "station_walk": 7,
            "bus_stops": 14,
            "safety_score": 68,
            "night_safety_score": 64,
            "flood_risk": "낮음",
            "flood_history": "대체로 낮음",
            "facilities": 78,
            "semi_basement_share": 13,
            "cctv_density": 72,
            "streetlight_density": 74,
            "one_room": 45,
            "officetel": 61,
            "villa": 49,
            "commute_gangnam": 50,
            "commute_hongdae": 32,
            "commute_jongno": 25,
            "commute_yeouido": 45,
            "commute_snu": 63,
            "caution": "도심 외 목적지라면 환승 시간을 확인",
            "reviews": ["북서권 생활비를 낮추기 좋음", "산책·주거 환경 선호자에게 맞음"],
        },
        {
            "dong": "혜화동",
            "district": "종로구",
            "lat": 37.5860,
            "lon": 127.0007,
            "deposit": 1500,
            "monthly_rent": 56,
            "station_walk": 7,
            "bus_stops": 15,
            "safety_score": 74,
            "night_safety_score": 70,
            "flood_risk": "낮음",
            "flood_history": "침수 리스크 낮음",
            "facilities": 86,
            "semi_basement_share": 11,
            "cctv_density": 78,
            "streetlight_density": 79,
            "one_room": 56,
            "officetel": 72,
            "villa": 60,
            "commute_gangnam": 40,
            "commute_hongdae": 32,
            "commute_jongno": 10,
            "commute_yeouido": 38,
            "commute_snu": 55,
            "caution": "대학로 상권 인접 매물은 야간 소음 확인",
            "reviews": ["종로·광화문 접근성이 좋음", "문화시설과 생활 편의가 많음"],
        },
        {
            "dong": "명동",
            "district": "중구",
            "lat": 37.5637,
            "lon": 126.9850,
            "deposit": 2000,
            "monthly_rent": 70,
            "station_walk": 5,
            "bus_stops": 18,
            "safety_score": 75,
            "night_safety_score": 70,
            "flood_risk": "낮음",
            "flood_history": "도심 중심부 침수 리스크 낮음",
            "facilities": 94,
            "semi_basement_share": 8,
            "cctv_density": 82,
            "streetlight_density": 84,
            "one_room": 70,
            "officetel": 92,
            "villa": 74,
            "commute_gangnam": 33,
            "commute_hongdae": 28,
            "commute_jongno": 8,
            "commute_yeouido": 25,
            "commute_snu": 48,
            "caution": "도심 상권 매물은 소음·관리비·실면적을 함께 확인",
            "reviews": ["중구 직장에는 출퇴근 부담이 낮음", "생활 편의는 좋지만 월세가 높은 편"],
        },
        {
            "dong": "상봉동",
            "district": "중랑구",
            "lat": 37.5967,
            "lon": 127.0858,
            "deposit": 1000,
            "monthly_rent": 44,
            "station_walk": 6,
            "bus_stops": 14,
            "safety_score": 67,
            "night_safety_score": 63,
            "flood_risk": "낮음",
            "flood_history": "대체로 낮음",
            "facilities": 78,
            "semi_basement_share": 13,
            "cctv_density": 71,
            "streetlight_density": 74,
            "one_room": 44,
            "officetel": 60,
            "villa": 48,
            "commute_gangnam": 45,
            "commute_hongdae": 50,
            "commute_jongno": 36,
            "commute_yeouido": 55,
            "commute_snu": 64,
            "caution": "월세는 낮지만 주요 업무지구 통근 시간이 길 수 있음",
            "reviews": ["역세권 생활은 편함", "통근 목적지를 먼저 확인해야 함"],
        },
    ]

    df = pd.DataFrame(rows)
    missing_districts = sorted(set(DISTRICT_CENTERS) - set(df["district"]))
    if missing_districts:
        raise ValueError(f"서울 구 데이터 누락: {', '.join(missing_districts)}")

    df["polygon"] = df.apply(lambda row: square_polygon(row["lat"], row["lon"]), axis=1)
    return df


def normalize_weights(night_priority: bool, convenience_priority: bool) -> dict[str, float]:
    weights = BASE_WEIGHTS.copy()
    if night_priority:
        weights["night_safety_score"] += 0.08
        weights["safety_score"] += 0.04
        weights["rent_score"] -= 0.07
        weights["transport_score"] -= 0.03
        weights["convenience_score"] -= 0.02
    if convenience_priority:
        weights["convenience_score"] += 0.07
        weights["rent_score"] -= 0.04
        weights["flood_score"] -= 0.03

    total = sum(weights.values())
    return {key: value / total for key, value in weights.items()}


def enrich_scores(
    df: pd.DataFrame,
    active_location: dict[str, object],
    night_priority: bool,
    convenience_priority: bool,
) -> pd.DataFrame:
    scored = df.copy()

    if active_location.get("commute_column") in scored.columns:
        scored["commute_min"] = scored[str(active_location["commute_column"])]
        scored["distance_km"] = scored.apply(
            lambda row: haversine_km(
                float(row["lat"]),
                float(row["lon"]),
                float(active_location["lat"]),
                float(active_location["lon"]),
            ),
            axis=1,
        )
    else:
        scored["commute_min"] = scored.apply(
            lambda row: estimate_commute_minutes(row, active_location),
            axis=1,
        )
        scored["distance_km"] = scored.apply(
            lambda row: haversine_km(
                float(row["lat"]),
                float(row["lon"]),
                float(active_location["lat"]),
                float(active_location["lon"]),
            ),
            axis=1,
        )

    scored["rent_score"] = (
        108 - scored["monthly_rent"] * 0.9 - scored["deposit"] * 0.006
    ).clip(35, 95)
    scored["transport_score"] = (
        104
        - scored["commute_min"] * 0.95
        - scored["station_walk"] * 1.8
        + scored["bus_stops"] * 0.45
    ).clip(35, 96)
    scored["flood_score"] = scored["flood_risk"].map(FLOOD_SCORE).fillna(60)
    scored["convenience_score"] = (scored["facilities"] * 0.88 + scored["bus_stops"] * 0.8).clip(
        35, 95
    )

    weights = normalize_weights(night_priority, convenience_priority)
    scored["survival_score"] = sum(scored[column] * weight for column, weight in weights.items())
    scored["survival_score"] = scored["survival_score"].round(0).astype(int)
    scored["value_index"] = (scored["survival_score"] / scored["monthly_rent"] * 10).round(1)
    scored["distance_km"] = scored["distance_km"].round(1)
    return scored


def score_class(score: int) -> str:
    if score >= 75:
        return "green"
    if score >= 65:
        return "yellow"
    return "red"


def score_label(score: int) -> str:
    if score >= 75:
        return "강력 추천"
    if score >= 65:
        return "검토 가능"
    return "주의 필요"


def map_color(score: int) -> list[int]:
    if score >= 75:
        return [35, 157, 114, 185]
    if score >= 65:
        return [217, 152, 47, 185]
    return [217, 95, 95, 185]


def current_theme_is_dark() -> bool:
    context = getattr(st, "context", None)
    theme = getattr(context, "theme", {}) if context is not None else {}
    return isinstance(theme, dict) and theme.get("type") == "dark"


def selected_theme_is_dark(theme_mode: str) -> bool:
    if theme_mode == "다크":
        return True
    if theme_mode == "라이트":
        return False
    return current_theme_is_dark()


def current_map_style(dark_mode: bool) -> str:
    if dark_mode:
        return "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
    return "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"


def map_text_color(dark_mode: bool) -> list[int]:
    return [240, 243, 246, 235] if dark_mode else [32, 37, 43, 230]


def target_color(dark_mode: bool) -> list[int]:
    return [116, 174, 232, 240] if dark_mode else [47, 111, 159, 235]


def chart_palette(dark_mode: bool) -> dict[str, str]:
    if dark_mode:
        return {
            "background": "#171b21",
            "plot": "#171b21",
            "text": "#ffffff",
            "muted": "#d7dee7",
            "grid": "#303844",
            "bar": "#74aee8",
            "bar_alt": "#3ecf98",
        }

    return {
        "background": "#ffffff",
        "plot": "#ffffff",
        "text": "#20252b",
        "muted": "#6b7280",
        "grid": "#e2ded3",
        "bar": "#2f6f9f",
        "bar_alt": "#239d72",
    }


def themed_bar_chart(
    data: pd.DataFrame,
    x: str,
    y: str,
    *,
    height: int,
    dark_mode: bool,
    bar_color: str | None = None,
) -> None:
    max_value = float(data[y].max()) if not data.empty else 1.0
    plot_height = max(130, height - 80)
    color = bar_color or "var(--blue)"

    columns = []
    labels = []
    for row in data.to_dict("records"):
        label = html.escape(str(row[x]))
        value = float(row[y])
        display_value = f"{value:.0f}"
        bar_height = 0 if max_value <= 0 else max(4, value / max_value * 100)
        columns.append(
            f'<div class="mini-chart-col" style="--bar-height:{bar_height:.2f}%;">'
            f'<span class="mini-chart-value">{display_value}</span>'
            '<div class="mini-chart-bar"></div>'
            '</div>'
        )
        labels.append(f'<div class="mini-chart-label">{label}</div>')

    chart_html = (
        f'<div class="mini-chart" style="--chart-height:{plot_height}px; --chart-bar:{color};">'
        f'<div class="mini-chart-plot">{"".join(columns)}</div>'
        f'<div class="mini-chart-labels">{"".join(labels)}</div>'
        f'<div class="mini-chart-axis-title">{html.escape(y)}</div>'
        '</div>'
    )

    st.markdown(
        chart_html,
        unsafe_allow_html=True,
    )


def apply_filters(
    df: pd.DataFrame,
    max_deposit: int,
    max_rent: int,
    commute_30: bool,
    station_10: bool,
    no_semibasement: bool,
    low_flood: bool,
    night_priority: bool,
    convenience_priority: bool,
) -> pd.DataFrame:
    filtered = df[(df["deposit"] <= max_deposit) & (df["monthly_rent"] <= max_rent)].copy()

    if commute_30:
        filtered = filtered[filtered["commute_min"] <= 30]
    if station_10:
        filtered = filtered[filtered["station_walk"] <= 10]
    if no_semibasement:
        filtered = filtered[filtered["semi_basement_share"] <= 14]
    if low_flood:
        filtered = filtered[filtered["flood_risk"] == "낮음"]
    if night_priority:
        filtered = filtered[filtered["night_safety_score"] >= 68]
    if convenience_priority:
        filtered = filtered[filtered["facilities"] >= 78]

    return filtered


def metric_card(label: str, value: str, helper: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <small>{html.escape(label)}</small>
            <strong>{html.escape(value)}</strong>
            <span>{html.escape(helper)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_rankings(ranking: pd.DataFrame) -> None:
    if ranking.empty:
        st.info("현재 조건에 맞는 동네가 없습니다.")
        return

    for idx, row in enumerate(ranking.itertuples(), start=1):
        st.markdown(
            f"""
            <div class="rank-row">
                <div class="rank-num">{idx}</div>
                <div>
                    <div class="rank-title">{html.escape(row.dong)}</div>
                    <div class="rank-meta">
                        {html.escape(row.district)} · 월세 {row.monthly_rent}만원 · 보증금 {row.deposit:,}만원 ·
                        통학/출근 {row.commute_min}분 · 목적지 {row.distance_km}km
                    </div>
                </div>
                <div class="score-pill {score_class(row.survival_score)}">{row.survival_score}점</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_map(
    map_df: pd.DataFrame,
    target_location: dict[str, object] | None,
    dark_mode: bool,
) -> None:
    deck_df = map_df.copy()
    deck_df["color"] = deck_df["survival_score"].apply(map_color)
    deck_df["label"] = deck_df.apply(
        lambda row: f"{row['dong']} {row['survival_score']}점",
        axis=1,
    )
    deck_df["risk_label"] = deck_df["survival_score"].apply(score_label)

    polygon_layer = pdk.Layer(
        "PolygonLayer",
        data=deck_df,
        get_polygon="polygon",
        get_fill_color="color",
        get_line_color=[255, 255, 255, 190],
        line_width_min_pixels=1,
        pickable=True,
        auto_highlight=True,
    )
    text_layer = pdk.Layer(
        "TextLayer",
        data=deck_df,
        get_position="[lon, lat]",
        get_text="label",
        get_size=13,
        get_color=map_text_color(dark_mode),
        get_text_anchor="'middle'",
        get_alignment_baseline="'center'",
        pickable=False,
    )

    layers = [polygon_layer, text_layer]
    if target_location is not None:
        target_df = pd.DataFrame(
            [
                {
                    "name": "목적지",
                    "lat": float(target_location["lat"]),
                    "lon": float(target_location["lon"]),
                }
            ]
        )
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=target_df,
                get_position="[lon, lat]",
                get_fill_color=target_color(dark_mode),
                get_line_color=[255, 255, 255, 255],
                get_radius=450,
                radius_min_pixels=7,
                line_width_min_pixels=2,
                pickable=False,
            )
        )
        layers.append(
            pdk.Layer(
                "TextLayer",
                data=target_df,
                get_position="[lon, lat]",
                get_text="name",
                get_size=15,
                get_color=target_color(dark_mode),
                get_pixel_offset=[0, -28],
                get_text_anchor="'middle'",
                get_alignment_baseline="'center'",
                pickable=False,
            )
    )

    st.pydeck_chart(
        pdk.Deck(
            map_style=current_map_style(dark_mode),
            initial_view_state=pdk.ViewState(
                latitude=37.545,
                longitude=126.985,
                zoom=10.35,
                pitch=0,
            ),
            layers=layers,
            tooltip={
                "html": (
                    "<b>{dong}</b><br/>"
                    "{district}<br/>"
                    "생존 점수 {survival_score}점 · {risk_label}<br/>"
                    "월세 {monthly_rent}만원 / 보증금 {deposit}만원<br/>"
                    "목적지 {distance_km}km · 통학/출근 {commute_min}분"
                ),
                "style": {
                    "backgroundColor": "#20252b",
                    "color": "#ffffff",
                    "fontSize": "12px",
                    "borderRadius": "8px",
                },
            },
        ),
        width="stretch",
        height=560,
    )


df_base = load_neighborhoods()
subway_stations = load_subway_stations()
subway_station_names = list(subway_stations.keys())

with st.sidebar:
    st.header("조건")
    theme_mode = st.radio(
        "화면 테마",
        ["시스템", "라이트", "다크"],
        index=0,
        horizontal=True,
    )
    st.divider()

    target_address = st.text_input("학교/직장 주소", placeholder="예: 서울 중구 을지로, 시청역, 강남역 11번 출구")
    fallback_anchor = st.selectbox(
        "주소를 못 찾을 때 사용할 기준지",
        subway_station_names,
        index=subway_station_names.index("강남역") if "강남역" in subway_station_names else 0,
    )
    max_deposit = st.slider("보증금 최대", 500, 4000, 2000, 100, format="%d만원")
    max_rent = st.slider("월세 최대", 35, 120, 70, 1, format="%d만원")

    st.divider()
    commute_30 = st.checkbox("학교/직장까지 30분 이내", value=False)
    station_10 = st.checkbox("지하철역 도보 10분", value=True)
    no_semibasement = st.checkbox("반지하 비중 낮은 곳", value=False)
    low_flood = st.checkbox("침수위험 낮음", value=False)
    night_priority = st.checkbox("밤길 안전 우선", value=False)
    convenience_priority = st.checkbox("편의점/마트 가까움", value=False)

    st.divider()
    st.caption(
        f"샘플 데이터 기준 · 서울 {df_base['district'].nunique()}개 구 · "
        f"기준지 {len(subway_station_names)}개 역"
    )

st.markdown(theme_override_css(theme_mode), unsafe_allow_html=True)
dark_mode = selected_theme_is_dark(theme_mode)

fallback_location = resolve_subway_station_location(fallback_anchor, subway_stations)
fallback_resolution_failed = fallback_location is None
if fallback_location is None:
    fallback_location = location_from_seed("강남역", ANCHOR_LOCATIONS["강남역"], "기본 기준지")

target_location = (
    geocode_target(target_address, df_base, subway_stations)
    if target_address.strip()
    else None
)
active_location = target_location or fallback_location
df = enrich_scores(df_base, active_location, night_priority, convenience_priority)
filtered = apply_filters(
    df,
    max_deposit,
    max_rent,
    commute_30,
    station_10,
    no_semibasement,
    low_flood,
    night_priority,
    convenience_priority,
)

display_df = filtered if not filtered.empty else df
ranking = filtered.sort_values("survival_score", ascending=False).head(10)
fallback_ranking = df.sort_values("survival_score", ascending=False).head(10)
basis_label = target_basis_label(active_location, fallback_anchor)

st.markdown(
    """
    <div class="hero">
        <h1>월세 생존 지도</h1>
        <p>
            학교나 직장 주소를 인식해 목적지 좌표를 잡고, 월세·교통·안전·침수·생활편의 데이터를 합쳐
            서울 25개 구 대표 동네의 자취 적합도를 비교합니다. 주소가 애매하면 서울 지하철역 전체 목록에서
            가장 가까운 기준지를 골라 계산할 수 있습니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
with metric_cols[0]:
    metric_card("조건 통과 동네", f"{len(filtered)}곳", basis_label)
with metric_cols[1]:
    if not filtered.empty:
        best = filtered.sort_values("survival_score", ascending=False).iloc[0]
        metric_card("추천 1순위", best["dong"], f"{best['survival_score']}점 · {score_label(best['survival_score'])}")
    else:
        metric_card("추천 1순위", "-", "조건을 조금 낮춰보세요")
with metric_cols[2]:
    avg_rent = int(filtered["monthly_rent"].mean()) if not filtered.empty else int(df["monthly_rent"].mean())
    metric_card("평균 월세", f"{avg_rent}만원", "조건 통과 기준")
with metric_cols[3]:
    metric_card("반영 구", f"{df_base['district'].nunique()}개", "서울 전체 구 대표값")

if target_address:
    safe_address = html.escape(target_address)
    if target_location is not None:
        source = html.escape(str(target_location.get("source", "주소 인식")))
        matched = html.escape(str(target_location.get("matched_text", target_location.get("name", ""))))
        name = html.escape(str(target_location.get("name", "")))
        district = html.escape(str(target_location.get("district", "")))
        st.markdown(
            f"""
            <div class="note">
                입력 주소 <b>{safe_address}</b>는 <b>{name}</b>({district})로 인식했습니다.
                매칭: {matched} · 방식: {source}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="warning">
                입력 주소 <b>{safe_address}</b>를 서울 내 위치로 찾지 못했습니다.
                현재는 <b>{html.escape(str(fallback_location['name']))}</b> 기준으로 계산합니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

if fallback_resolution_failed:
    st.markdown(
        f"""
        <div class="warning">
            선택한 기준지 <b>{html.escape(fallback_anchor)}</b>의 좌표를 찾지 못해
            기본값인 <b>강남역</b> 기준으로 계산합니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

if filtered.empty:
    st.warning("선택한 조건에 맞는 동네가 없습니다. 지도는 전체 동네 기준으로 표시합니다.")

map_col, rank_col = st.columns([1.45, 1])
with map_col:
    st.subheader("주소 기준 월세 지도")
    st.markdown(
        """
        <div class="legend">
            <span class="legend-item"><span class="dot green"></span>초록: 강력 추천</span>
            <span class="legend-item"><span class="dot yellow"></span>노랑: 검토 가능</span>
            <span class="legend-item"><span class="dot red"></span>빨강: 주의 필요</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_map(display_df, active_location, dark_mode)

with rank_col:
    st.subheader("내 예산에 맞는 동네 TOP 10")
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    render_rankings(ranking if not ranking.empty else fallback_ranking)
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

detail_options = (
    ranking["dong"].tolist()
    if not ranking.empty
    else fallback_ranking["dong"].tolist()
)
selected_dong = st.selectbox("동네 상세", detail_options)
selected = df[df["dong"] == selected_dong].iloc[0]

detail_col, score_col = st.columns([1.15, 0.85])
with detail_col:
    st.subheader(f"{selected['dong']} 상세")
    st.markdown(
        f"""
        <div class="panel">
            <div class="section-label">월세 생존 점수</div>
            <h3 style="margin:0;">{selected['survival_score']}점 · {score_label(int(selected['survival_score']))}</h3>
            <p style="color:var(--muted); margin-top:0.45rem;">
                월세 {selected['monthly_rent']}만원 · 보증금 {selected['deposit']:,}만원 ·
                역 도보 {selected['station_walk']}분 · 통학/출근 {selected['commute_min']}분 · 목적지 {selected['distance_km']}km
            </p>
            <div class="warning">{html.escape(selected['caution'])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with score_col:
    st.subheader("점수 구성")
    score_breakdown = pd.DataFrame(
        {
            "항목": ["월세 부담", "교통 접근성", "안전", "침수 위험", "생활편의", "밤길 안심"],
            "점수": [
                int(selected["rent_score"]),
                int(selected["transport_score"]),
                int(selected["safety_score"]),
                int(selected["flood_score"]),
                int(selected["convenience_score"]),
                int(selected["night_safety_score"]),
            ],
        }
    )
    themed_bar_chart(
        score_breakdown,
        x="항목",
        y="점수",
        height=250,
        dark_mode=dark_mode,
        bar_color="var(--green)",
    )

price_tab, safety_tab, life_tab, community_tab = st.tabs(
    ["전월세", "안전·침수", "생활권", "자취 후기"]
)

with price_tab:
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 최근 전월세 실거래가 분포")
        rent_distribution = pd.DataFrame(
            {
                "구간": ["하위 25%", "중앙값", "상위 25%"],
                "월세(만원)": [
                    max(35, int(selected["monthly_rent"] - 8)),
                    int(selected["monthly_rent"]),
                    int(selected["monthly_rent"] + 12),
                ],
            }
        )
        themed_bar_chart(
            rent_distribution,
            x="구간",
            y="월세(만원)",
            height=260,
            dark_mode=dark_mode,
        )
    with col_b:
        st.markdown("#### 주거 유형별 평균 월세")
        type_rents = pd.DataFrame(
            {
                "주거 유형": ["원룸", "오피스텔", "빌라"],
                "평균 월세(만원)": [
                    int(selected["one_room"]),
                    int(selected["officetel"]),
                    int(selected["villa"]),
                ],
            }
        )
        themed_bar_chart(
            type_rents,
            x="주거 유형",
            y="평균 월세(만원)",
            height=260,
            dark_mode=dark_mode,
        )

with safety_tab:
    safety_cols = st.columns(4)
    safety_cols[0].metric("CCTV 밀도", f"{int(selected['cctv_density'])}점")
    safety_cols[1].metric("가로등 밀도", f"{int(selected['streetlight_density'])}점")
    safety_cols[2].metric("침수 위험", selected["flood_risk"])
    safety_cols[3].metric("반지하 비중", f"{int(selected['semi_basement_share'])}%")
    st.markdown(
        f"""
        <div class="note">
            침수 이력: {html.escape(selected['flood_history'])}
        </div>
        """,
        unsafe_allow_html=True,
    )

with life_tab:
    life_cols = st.columns(4)
    life_cols[0].metric("생활시설 개수", f"{int(selected['facilities'])}개")
    life_cols[1].metric("버스정류장", f"{int(selected['bus_stops'])}개")
    life_cols[2].metric("역까지 평균", f"{int(selected['station_walk'])}분")
    life_cols[3].metric("가성비 지수", f"{selected['value_index']}")

    value_ranking = df.sort_values("value_index", ascending=False).head(8)[
        ["district", "dong", "monthly_rent", "commute_min", "survival_score", "value_index"]
    ]
    value_ranking = value_ranking.rename(
        columns={
            "district": "구",
            "dong": "동네",
            "monthly_rent": "월세",
            "commute_min": "통근",
            "survival_score": "생존 점수",
            "value_index": "가성비 지수",
        }
    )
    st.dataframe(value_ranking, hide_index=True, width="stretch")

with community_tab:
    if "notes" not in st.session_state:
        st.session_state.notes = []

    with st.form("community_form", clear_on_submit=True):
        note = st.text_area(
            "자취 후기/주의사항",
            placeholder="예: 밤에는 큰길 위주로 다니는 게 편했어요.",
            height=90,
        )
        submitted = st.form_submit_button("등록")
        if submitted and note.strip():
            st.session_state.notes.insert(
                0,
                {
                    "dong": selected_dong,
                    "note": note.strip(),
                },
            )

    st.markdown("#### 이 동네에서 조심할 점")
    st.markdown(f'<div class="warning">{html.escape(selected["caution"])}</div>', unsafe_allow_html=True)

    st.markdown("#### 후기")
    for review in selected["reviews"]:
        st.markdown(f'<div class="note">{html.escape(review)}</div>', unsafe_allow_html=True)

    for item in st.session_state.notes:
        if item["dong"] == selected_dong:
            st.markdown(f'<div class="note">{html.escape(item["note"])}</div>', unsafe_allow_html=True)

st.caption("월세 생존 지도 · Streamlit MVP · 서울 25개 구 대표 샘플 데이터")
