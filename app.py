from __future__ import annotations

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
        --paper: #f7f5ef;
        --ink: #20252b;
        --muted: #6b7280;
        --line: #e2ded3;
        --green: #239d72;
        --yellow: #d9982f;
        --red: #d95f5f;
        --blue: #2f6f9f;
    }

    .stApp {
        background: var(--paper);
        color: var(--ink);
    }

    .block-container {
        padding-top: 1.4rem;
        padding-bottom: 2.5rem;
        max-width: 1240px;
    }

    [data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid var(--line);
    }

    h1, h2, h3 {
        letter-spacing: 0;
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
        max-width: 760px;
        color: var(--muted);
        font-size: 1.02rem;
        line-height: 1.65;
        margin: 0;
    }

    .metric-card {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem;
        min-height: 112px;
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
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem;
    }

    .rank-row {
        display: grid;
        grid-template-columns: 2.2rem 1fr auto;
        gap: 0.75rem;
        align-items: center;
        padding: 0.8rem 0;
        border-bottom: 1px solid #ece8dd;
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
        background: #f0ece2;
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
        background: #f3f8fa;
        padding: 0.75rem 0.85rem;
        border-radius: 6px;
        margin: 0.55rem 0;
        color: #26323a;
    }

    .warning {
        border-left: 4px solid var(--red);
        background: #fff5f3;
        padding: 0.75rem 0.85rem;
        border-radius: 6px;
        margin: 0.55rem 0;
        color: #4b2f2d;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 0.75rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


BASE_WEIGHTS = {
    "rent_score": 0.28,
    "transport_score": 0.22,
    "safety_score": 0.18,
    "flood_score": 0.16,
    "convenience_score": 0.10,
    "night_safety_score": 0.06,
}

ANCHORS = {
    "강남역": "commute_gangnam",
    "홍대입구역": "commute_hongdae",
    "종로": "commute_jongno",
    "여의도": "commute_yeouido",
    "서울대입구": "commute_snu",
}


def square_polygon(lat: float, lon: float, size: float = 0.0075) -> list[list[float]]:
    return [
        [lon - size, lat - size * 0.72],
        [lon + size, lat - size * 0.72],
        [lon + size, lat + size * 0.72],
        [lon - size, lat + size * 0.72],
    ]


@st.cache_data
def load_neighborhoods() -> pd.DataFrame:
    rows = [
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
            "dong": "봉천동",
            "district": "관악구",
            "lat": 37.4826,
            "lon": 126.9519,
            "deposit": 1500,
            "monthly_rent": 52,
            "station_walk": 9,
            "bus_stops": 12,
            "safety_score": 66,
            "night_safety_score": 64,
            "flood_risk": "낮음",
            "flood_history": "뚜렷한 반복 침수 이력 낮음",
            "facilities": 73,
            "semi_basement_share": 16,
            "cctv_density": 72,
            "streetlight_density": 70,
            "one_room": 52,
            "officetel": 68,
            "villa": 55,
            "commute_gangnam": 30,
            "commute_hongdae": 40,
            "commute_jongno": 44,
            "commute_yeouido": 35,
            "commute_snu": 6,
            "caution": "언덕 매물과 지하철 접근 시간을 실제 도보로 확인",
            "reviews": ["서울대입구 접근성이 강점", "언덕 위 매물은 겨울 동선이 불편"],
        },
        {
            "dong": "연남동",
            "district": "마포구",
            "lat": 37.5625,
            "lon": 126.9238,
            "deposit": 2000,
            "monthly_rent": 68,
            "station_walk": 10,
            "bus_stops": 11,
            "safety_score": 75,
            "night_safety_score": 70,
            "flood_risk": "낮음",
            "flood_history": "침수 리스크 낮음",
            "facilities": 91,
            "semi_basement_share": 11,
            "cctv_density": 78,
            "streetlight_density": 80,
            "one_room": 68,
            "officetel": 86,
            "villa": 70,
            "commute_gangnam": 43,
            "commute_hongdae": 8,
            "commute_jongno": 32,
            "commute_yeouido": 31,
            "commute_snu": 47,
            "caution": "생활 만족도는 높지만 월세와 주말 소음을 확인",
            "reviews": ["편의시설과 카페가 많음", "밤 시간 유동인구가 많아 호불호 있음"],
        },
        {
            "dong": "망원동",
            "district": "마포구",
            "lat": 37.5568,
            "lon": 126.91,
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
            "dong": "성수동",
            "district": "성동구",
            "lat": 37.5446,
            "lon": 127.0557,
            "deposit": 3000,
            "monthly_rent": 82,
            "station_walk": 8,
            "bus_stops": 10,
            "safety_score": 82,
            "night_safety_score": 78,
            "flood_risk": "낮음",
            "flood_history": "주요 주거지 침수 리스크 낮음",
            "facilities": 86,
            "semi_basement_share": 8,
            "cctv_density": 82,
            "streetlight_density": 86,
            "one_room": 82,
            "officetel": 105,
            "villa": 84,
            "commute_gangnam": 25,
            "commute_hongdae": 35,
            "commute_jongno": 28,
            "commute_yeouido": 38,
            "commute_snu": 48,
            "caution": "월세 부담이 높고 인기 상권 주변은 소음 확인",
            "reviews": ["안전 체감은 좋은 편", "예산 여유가 있을 때 만족도 높음"],
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
            "dong": "공덕동",
            "district": "마포구",
            "lat": 37.5443,
            "lon": 126.9512,
            "deposit": 3000,
            "monthly_rent": 78,
            "station_walk": 6,
            "bus_stops": 17,
            "safety_score": 80,
            "night_safety_score": 77,
            "flood_risk": "낮음",
            "flood_history": "역세권 중심부 침수 리스크 낮음",
            "facilities": 92,
            "semi_basement_share": 7,
            "cctv_density": 86,
            "streetlight_density": 84,
            "one_room": 78,
            "officetel": 98,
            "villa": 80,
            "commute_gangnam": 38,
            "commute_hongdae": 18,
            "commute_jongno": 22,
            "commute_yeouido": 14,
            "commute_snu": 45,
            "caution": "교통은 뛰어나지만 월세와 관리비가 높음",
            "reviews": ["직장인에게 동선이 편함", "예산 상한을 넉넉히 잡아야 함"],
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
        {
            "dong": "독산동",
            "district": "금천구",
            "lat": 37.4692,
            "lon": 126.897,
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
    ]

    df = pd.DataFrame(rows)
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
    anchor_column: str,
    night_priority: bool,
    convenience_priority: bool,
) -> pd.DataFrame:
    scored = df.copy()
    scored["commute_min"] = scored[anchor_column]
    scored["rent_score"] = (
        108 - scored["monthly_rent"] * 0.9 - scored["deposit"] * 0.006
    ).clip(35, 95)
    scored["transport_score"] = (
        104
        - scored["commute_min"] * 0.95
        - scored["station_walk"] * 1.8
        + scored["bus_stops"] * 0.45
    ).clip(35, 96)
    scored["flood_score"] = scored["flood_risk"].map({"낮음": 90, "보통": 64, "높음": 38})
    scored["convenience_score"] = (scored["facilities"] * 0.88 + scored["bus_stops"] * 0.8).clip(
        35, 95
    )

    weights = normalize_weights(night_priority, convenience_priority)
    scored["survival_score"] = sum(scored[column] * weight for column, weight in weights.items())
    scored["survival_score"] = scored["survival_score"].round(0).astype(int)
    scored["value_index"] = (scored["survival_score"] / scored["monthly_rent"] * 10).round(1)
    return scored


def score_class(score: int) -> str:
    if score >= 75:
        return "green"
    if score >= 65:
        return "yellow"
    return "red"


def score_label(score: int) -> str:
    if score >= 75:
        return "가성비 좋음"
    if score >= 65:
        return "보통"
    return "리스크 높음"


def map_color(score: int) -> list[int]:
    if score >= 75:
        return [35, 157, 114, 185]
    if score >= 65:
        return [217, 152, 47, 185]
    return [217, 95, 95, 185]


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
            <small>{label}</small>
            <strong>{value}</strong>
            <span>{helper}</span>
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
                    <div class="rank-title">{row.dong}</div>
                    <div class="rank-meta">
                        {row.district} · 월세 {row.monthly_rent}만원 · 보증금 {row.deposit:,}만원 ·
                        통학/출근 {row.commute_min}분
                    </div>
                </div>
                <div class="score-pill {score_class(row.survival_score)}">{row.survival_score}점</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_map(map_df: pd.DataFrame) -> None:
    deck_df = map_df.copy()
    deck_df["color"] = deck_df["survival_score"].apply(map_color)
    deck_df["label"] = deck_df.apply(
        lambda row: f"{row['dong']} {row['survival_score']}점", axis=1
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
        get_color=[32, 37, 43, 230],
        get_angle=0,
        get_text_anchor="'middle'",
        get_alignment_baseline="'center'",
        pickable=False,
    )

    st.pydeck_chart(
        pdk.Deck(
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            initial_view_state=pdk.ViewState(
                latitude=37.545,
                longitude=126.985,
                zoom=10.35,
                pitch=0,
            ),
            layers=[polygon_layer, text_layer],
            tooltip={
                "html": (
                    "<b>{dong}</b><br/>"
                    "{district}<br/>"
                    "생존 점수 {survival_score}점 · {risk_label}<br/>"
                    "월세 {monthly_rent}만원 / 보증금 {deposit}만원<br/>"
                    "역 도보 {station_walk}분 · 통학/출근 {commute_min}분"
                ),
                "style": {
                    "backgroundColor": "#20252b",
                    "color": "#ffffff",
                    "fontSize": "12px",
                    "borderRadius": "8px",
                },
            },
        ),
        use_container_width=True,
        height=560,
    )


df_base = load_neighborhoods()

with st.sidebar:
    st.header("조건")
    target_address = st.text_input("학교/직장 주소", placeholder="예: 강남역 11번 출구")
    anchor = st.selectbox("가까운 기준지", list(ANCHORS.keys()))
    max_deposit = st.slider("보증금 최대", 500, 4000, 2000, 100, format="%d만원")
    max_rent = st.slider("월세 최대", 35, 100, 65, 1, format="%d만원")

    st.divider()
    commute_30 = st.checkbox("학교/직장까지 30분 이내", value=False)
    station_10 = st.checkbox("지하철역 도보 10분", value=True)
    no_semibasement = st.checkbox("반지하 제외", value=False)
    low_flood = st.checkbox("침수위험 낮음", value=False)
    night_priority = st.checkbox("밤길 안전 우선", value=False)
    convenience_priority = st.checkbox("편의점/마트 가까움", value=False)

    st.divider()
    st.caption("샘플 데이터 기준")

anchor_column = ANCHORS[anchor]
df = enrich_scores(df_base, anchor_column, night_priority, convenience_priority)
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

st.markdown(
    """
    <div class="hero">
        <h1>월세 생존 지도</h1>
        <p>
            월세, 교통, 안전, 침수, 생활편의 데이터를 합쳐 자취생에게
            진짜 살 만한 동네를 추천합니다.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_cols = st.columns(4)
with metric_cols[0]:
    metric_card("조건 통과 동네", f"{len(filtered)}곳", f"{anchor} 기준")
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
    risk_count = int((filtered["survival_score"] < 65).sum()) if not filtered.empty else 0
    metric_card("리스크 높은 동네", f"{risk_count}곳", "65점 미만")

if target_address:
    st.markdown(
        f"""
        <div class="note">
            입력 주소 <b>{target_address}</b>는 <b>{anchor}</b> 권역으로 보고 통학·출근 시간을 계산했습니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

if filtered.empty:
    st.warning("선택한 조건에 맞는 동네가 없습니다. 지도는 전체 동네 기준으로 표시합니다.")

map_col, rank_col = st.columns([1.45, 1])
with map_col:
    st.subheader("동 단위 월세 지도")
    st.markdown(
        """
        <div class="legend">
            <span class="legend-item"><span class="dot green"></span>초록: 가성비 좋음</span>
            <span class="legend-item"><span class="dot yellow"></span>노랑: 보통</span>
            <span class="legend-item"><span class="dot red"></span>빨강: 리스크 높음</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    render_map(display_df)

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
            <h3 style="margin:0;">{selected['survival_score']}점 · {score_label(selected['survival_score'])}</h3>
            <p style="color:#6b7280; margin-top:0.45rem;">
                월세 {selected['monthly_rent']}만원 · 보증금 {selected['deposit']:,}만원 ·
                역 도보 {selected['station_walk']}분 · 통학/출근 {selected['commute_min']}분
            </p>
            <div class="warning">{selected['caution']}</div>
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
    st.bar_chart(score_breakdown, x="항목", y="점수", height=250)

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
        st.bar_chart(rent_distribution, x="구간", y="월세(만원)", height=260)
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
        st.bar_chart(type_rents, x="주거 유형", y="평균 월세(만원)", height=260)

with safety_tab:
    safety_cols = st.columns(4)
    safety_cols[0].metric("CCTV 밀도", f"{int(selected['cctv_density'])}점")
    safety_cols[1].metric("가로등 밀도", f"{int(selected['streetlight_density'])}점")
    safety_cols[2].metric("침수 위험", selected["flood_risk"])
    safety_cols[3].metric("반지하 비중", f"{int(selected['semi_basement_share'])}%")
    st.markdown(
        f"""
        <div class="note">
            침수 이력: {selected['flood_history']}
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

    value_ranking = df.sort_values("value_index", ascending=False).head(6)[
        ["dong", "monthly_rent", "survival_score", "value_index"]
    ]
    value_ranking = value_ranking.rename(
        columns={
            "dong": "동네",
            "monthly_rent": "월세",
            "survival_score": "생존 점수",
            "value_index": "가성비 지수",
        }
    )
    st.dataframe(value_ranking, hide_index=True, use_container_width=True)

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
    st.markdown(f'<div class="warning">{selected["caution"]}</div>', unsafe_allow_html=True)

    st.markdown("#### 후기")
    for review in selected["reviews"]:
        st.markdown(f'<div class="note">{review}</div>', unsafe_allow_html=True)

    for item in st.session_state.notes:
        if item["dong"] == selected_dong:
            st.markdown(f'<div class="note">{item["note"]}</div>', unsafe_allow_html=True)

st.caption("월세 생존 지도 · Streamlit MVP")
