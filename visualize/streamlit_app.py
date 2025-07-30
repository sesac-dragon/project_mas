from total_map_data import load_place_summary_with_location
from wordcloud import WordCloud
from collections import Counter
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
from streamlit_folium import st_folium
import folium
from sqlalchemy.orm import sessionmaker
from common.db_connection import get_engine
from common.db_table import Review, ReviewAnalysis,Restaurant  
from datetime import datetime, timedelta
from sklearn.cluster import KMeans
from openai import OpenAI
import altair as alt
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path="/app/.env")
import re

            

# 나눔글꼴 경로 자동 탐색
font_path = '/usr/share/fonts/truetype/nanum/NanumGothic.ttf'
plt.rc('font', family=fm.FontProperties(fname=font_path).get_name())

# 마이너 경고 제거 (minus 깨짐 방지용)
plt.rcParams['axes.unicode_minus'] = False



st.set_page_config(page_title="카카오맵 맛집 대쉬보드", layout="wide")

st.title("카카오맵 맛집 리뷰 대시보드")
st.markdown("리뷰 감성 분석 및 통계 시각화를 통해 MZ세대의 광고없는 진짜 맛집을 데이터로 분석합니다.")

#데이터 로드
@st.cache_data
def load_data():
  return load_place_summary_with_location()

df = load_data()

# 사이드바 메뉴
st.sidebar.title("분석 항목")
menu = st.sidebar.radio("메뉴 선택", [
  "1. 평점 기반 통계",
  "2. 감성 분석 기반 추천",
  "3. 리뷰 키워드 분석 추천",
  "4. 지도 기반 시각화",
  "5. 시간 흐름 분석 추천",
  "6. 신뢰도 분석",
  "7. 주인장의 음식점 추천"
])


if menu == "1. 평점 기반 통계":
    st.header(" 평점 기반 음식점 Top 10")

    plt.rcParams['font.family'] = 'NanumGothic'
    plt.rcParams['axes.unicode_minus'] = False
    sns.set(font="NanumGothic")

    top10 = df.sort_values(by="rating_average", ascending=False).head(10).copy()

    # 정규화된 리뷰 수 및 긍정 비율 추가
    top10["리뷰수_정규화"] = top10["rating_count"] / top10["rating_count"].max()
    top10["긍정비율_정규화"] = top10["positive_ratio"] / top10["positive_ratio"].max()

    fig, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.25
    index = np.arange(len(top10))

    bar1 = ax.bar(index, top10["rating_average"], bar_width, label=" 평점", color="skyblue")
    bar2 = ax.bar(index + bar_width, top10["리뷰수_정규화"], bar_width, label=" 리뷰 수(정규화)", color="orange")
    bar3 = ax.bar(index + 2 * bar_width, top10["긍정비율_정규화"], bar_width, label=" 긍정 비율(정규화)", color="lightgreen")

    ax.set_xticks(index + bar_width)
    ax.set_xticklabels(top10["restaurant_name"], rotation=45, ha="right")
    ax.set_title("Top10 음식점 평점/리뷰수/긍정비율 비교")
    ax.legend()
    st.pyplot(fig)

    st.markdown("가장 평점이 높은 음식점 상위 10개를 평점/리뷰 수/긍정비율로 비교한 바 차트입니다.")

    st.subheader(" Top 10 음식점 상세 정보")
    top_display = top10[[
        "restaurant_name", "address", "rating_average", "rating_count", "positive_ratio", "top_keywords"
    ]].rename(columns={
        "restaurant_name": "이름",
        "address": "주소",
        "rating_average": "평균 평점",
        "rating_count": "리뷰 수",
        "positive_ratio": "긍정 비율",
        "top_keywords": "대표 키워드"
    })
    st.dataframe(top_display, use_container_width=True)

    st.divider()
    st.header(" 평점 낮은 음식점 Bottom 10")

    bottom10 = df[df["rating_average"] > 0].sort_values(by="rating_average", ascending=True).head(10).copy()

    bottom10["리뷰수_정규화"] = bottom10["rating_count"] / bottom10["rating_count"].max()
    bottom10["긍정비율_정규화"] = bottom10["positive_ratio"] / bottom10["positive_ratio"].max()

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    bar_width = 0.25
    index = np.arange(len(bottom10))

    ax2.bar(index, bottom10["rating_average"], bar_width, label=" 평점", color="skyblue")
    ax2.bar(index + bar_width, bottom10["리뷰수_정규화"], bar_width, label=" 리뷰 수(정규화)", color="orange")
    ax2.bar(index + 2 * bar_width, bottom10["긍정비율_정규화"], bar_width, label=" 긍정 비율(정규화)", color="lightgreen")

    ax2.set_xticks(index + bar_width)
    ax2.set_xticklabels(bottom10["restaurant_name"], rotation=45, ha="right")
    ax2.set_title("Bottom10 음식점 평점/리뷰수/긍정비율 비교")
    ax2.legend()
    st.pyplot(fig2)

    st.subheader(" Bottom 10 음식점 상세 정보")
    bottom_display = bottom10[[
        "restaurant_name", "address", "rating_average", "rating_count", "positive_ratio", "top_keywords"
    ]].rename(columns={
        "restaurant_name": "이름",
        "address": "주소",
        "rating_average": "평균 평점",
        "rating_count": "리뷰 수",
        "positive_ratio": "긍정 비율",
        "top_keywords": "대표 키워드"
    })
    st.dataframe(bottom_display, use_container_width=True)


if menu == "2. 감성 분석 기반 추천":
    st.header(" 긍정 비율 Top 10 음식점 (리뷰수, 평점 고려 시각화)")
    top10_pos = df.sort_values(by="positive_ratio", ascending=False).head(10)
    top10_pos["리뷰수 등급"] = pd.cut(top10_pos["rating_count"], bins=[0, 5, 20, 100, 10000], labels=["낮음", "보통", "높음", "매우높음"])

    st.subheader("긍정 비율 / 리뷰 수 / 평균 평점을 고려한 점 그래프")
    chart1 = alt.Chart(top10_pos).mark_circle(size=200).encode(
        x=alt.X("rating_count", title="리뷰 수"),
        y=alt.Y("positive_ratio", title="긍정 비율"),
        color=alt.Color("rating_average", scale=alt.Scale(scheme="blues"), title="평균 평점"),
        tooltip=["restaurant_name", "address", "rating_count", "positive_ratio", "rating_average"]
    ).properties(width=800, height=400)
    st.altair_chart(chart1, use_container_width=True, key="chart2_pos_top10")

    st.subheader("해당 음식점 키워드 워드클라우드")
    keyword_text = ", ".join(top10_pos["top_keywords"].dropna().tolist())
    wordcloud = WordCloud(
        font_path="/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        width=800, height=400, background_color="white"
    ).generate(keyword_text)

    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)  #  key 제거

    st.divider()

    st.header(" 부정 평가 음식점 Top 10 (긍정 비율 낮음)")
    bottom10_pos = df[df["total"] >= 10].sort_values(by="positive_ratio", ascending=True).head(10)

    st.subheader(" 부정 Top10 음식점 점 그래프")
    chart2 = alt.Chart(bottom10_pos).mark_circle(size=200).encode(
        x=alt.X("rating_count", title="리뷰 수"),
        y=alt.Y("positive_ratio", title="긍정 비율"),
        color=alt.Color("rating_average", scale=alt.Scale(scheme="oranges"), title="평균 평점"),
        tooltip=["restaurant_name", "address", "rating_count", "positive_ratio", "rating_average"]
    ).properties(width=800, height=400)
    st.altair_chart(chart2, use_container_width=True, key="chart2_neg_top10")

    st.subheader(" 해당 음식점 키워드 워드클라우드 (부정 Top10)")
    negative_keyword_text = ", ".join(bottom10_pos["top_keywords"].dropna().tolist())
    neg_wordcloud = WordCloud(
        font_path="/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        width=800, height=400, background_color="white", colormap="Reds"
    ).generate(negative_keyword_text)

    fig2, ax2 = plt.subplots()
    ax2.imshow(neg_wordcloud, interpolation='bilinear')
    ax2.axis("off")
    st.pyplot(fig2)  #  key 제거

    st.subheader(" 음식점 상세 정보 (긍정 Top10 & 부정 Top10)")
    display_cols = ["restaurant_name", "address", "rating_average", "rating_count", "positive_ratio", "top_keywords"]
    display_df = pd.concat([top10_pos, bottom10_pos])[display_cols].rename(columns={
        "restaurant_name": "이름", "address": "주소",
        "rating_average": "평균 평점", "rating_count": "리뷰 수",
        "positive_ratio": "긍정 비율", "top_keywords": "대표 키워드"
    })
    st.dataframe(display_df, use_container_width=True, key="df2_pos_neg_detail")





elif menu == "3. 리뷰 키워드 분석 추천":
    st.header(" 리뷰 키워드 분석")

    import re
    from collections import Counter

    #  키워드 분리: 쉼표 기준으로 분할하고 strip 처리
    all_keywords = df["top_keywords"].dropna().apply(
        lambda x: [kw.strip() for kw in re.split(r",\s*", x) if kw.strip()]
    )
    flat_keywords = [kw for sublist in all_keywords for kw in sublist]
    kw_counter = Counter(flat_keywords)

    #  Top 20 키워드
    st.subheader(" 리뷰에서 자주 언급된 키워드 Top 20")
    keyword_df = pd.DataFrame(kw_counter.items(), columns=["keyword", "count"])
    keyword_df = keyword_df.sort_values("count", ascending=False).head(20)

    chart = alt.Chart(keyword_df).mark_circle(size=200).encode(
        x=alt.X("keyword", sort="-y", title="키워드"),
        y=alt.Y("count", title="언급 횟수"),
        color=alt.Color("count", scale=alt.Scale(scheme='blues')),
        tooltip=["keyword", "count"]
    ).properties(width=800, height=400)

    st.altair_chart(chart, use_container_width=True, key="chart3_kw_top20")

    # 특정 키워드 검색
    st.subheader(" 특정 키워드 언급 음식점 찾기")
    selected_keyword = st.selectbox("검색할 키워드 선택", [""] + keyword_df["keyword"].tolist())

    if selected_keyword:
        keyword_filtered = df[df["top_keywords"].fillna("").str.contains(selected_keyword)]
        st.markdown(f"**'{selected_keyword}' 키워드가 포함된 음식점 리스트**")

        display_df = keyword_filtered[[
            "restaurant_name", "address", "rating_average", "rating_count", "positive_ratio", "top_keywords"
        ]].rename(columns={
            "restaurant_name": "이름", "address": "주소",
            "rating_average": "평균 평점", "rating_count": "리뷰 수",
            "positive_ratio": "긍정 비율", "top_keywords": "대표 키워드"
        })

        st.dataframe(display_df, use_container_width=True, key="df3_kw_filtered")

    st.divider()

    # 음식점별 키워드 수 분포
    st.subheader(" 음식점별 키워드 수 분포")

    df["keyword_count"] = df["top_keywords"].fillna("").apply(
        lambda x: len([kw.strip() for kw in re.split(r",\s*", x) if kw.strip()])
    )
    keyword_count_df = df[df["rating_count"] >= 10].copy()

    chart2 = alt.Chart(keyword_count_df).mark_circle(opacity=0.7).encode(
        x=alt.X("rating_average", title="평균 평점"),
        y=alt.Y("keyword_count", title="키워드 수"),
        size=alt.Size("rating_count", title="리뷰 수"),
        color=alt.Color("positive_ratio", title="긍정 비율", scale=alt.Scale(scheme="greenblue")),
        tooltip=["restaurant_name", "rating_average", "keyword_count", "rating_count", "positive_ratio"]
    ).properties(width=800, height=500)

    st.altair_chart(chart2, use_container_width=True, key="chart3_kw_count")





elif menu == "4. 지도 기반 시각화":
    st.header("음식점 지도 시각화 ")
    st.markdown("지도의 확드/추소 또는 이동에 따라 보이는 음식점만 실시간 표시합니다.")

    center_lat = df["lat"].mean()
    center_lon = df["lon"].mean()
    st_data = {}

    bounds = st_data.get("bounds", {})
    if "_southWest" in bounds and "_northEast" in bounds:
        sw = bounds["_southWest"]
        ne = bounds["_northEast"]
        visible_df = df[
            (df["lat"] >= sw["lat"]) & (df["lat"] <= ne["lat"]) &
            (df["lon"] >= sw["lng"]) & (df["lon"] <= ne["lng"])
        ]
    else:
        visible_df = df

    visible_df = visible_df.copy()
    st.markdown(f"현재 지도 내 음식점 수: **{len(visible_df)}개**")

    zoom = st_data.get("zoom", 12)
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom)

    def get_color(rating):
        if rating >= 4.5:
            return "green"
        elif rating >= 4.0:
            return "blue"
        elif rating >= 3.0:
            return "orange"
        else:
            return "red"

    # 할플레이스 Circle (추가기능 없음)
    hot_df = visible_df[(visible_df["rating_average"] >= 4.3) & (visible_df["positive_ratio"] >= 0.75)]
    coords = hot_df[["lat", "lon"]]

    if len(coords) >= 3:
        kmeans = KMeans(n_clusters=3, random_state=42).fit(coords)
        centers = pd.DataFrame(kmeans.cluster_centers_, columns=["lat", "lon"])

        for _, row in centers.iterrows():
            folium.Circle(
                location=[row["lat"], row["lon"]],
                radius=300,
                color="red",
                fill=True,
                fill_opacity=0.2,
                tooltip=None,
                popup=None  # popup 바로 삭제해야 복잡한 화면이 안나온다.
            ).add_to(m)

        st.markdown("현재 지도 내 평점 4.3 이상 & 강정 75% 이상 음식점이 미일집되는 할플레이스입니다.")
    else:
        st.info("할플레이스를 표시할 수 있을 만큼의 음식점이 지도 내에 충분하지 않습니다.")

    # 음식점 마커
    for _, row in visible_df.iterrows():
        popup_text = f"""
        <b>{row['restaurant_name']}</b><br>
        {row['address']}<br>
        평점: {row['rating_average']}<br>
        키워드: {row['top_keywords'] or '없음'}
        """
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=5,
            color=get_color(row["rating_average"]),
            fill=True,
            fill_opacity=0.7,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=row["restaurant_name"]
        ).add_to(m)

    st_folium(m, width=1000, height=600, key="map_final")












elif menu == "5. 시간 흐름 분석 추천":
    st.header(" 평점 또는 감정 급상승 음식점 Top10")

    # 분석 기준 기간 선택
    period_option = st.selectbox("분석 기준 기간", ["1개월", "3개월", "1년"])

    # 기간 계산
    now = datetime.now()
    if period_option == "1개월":
        delta = timedelta(days=30)
    elif period_option == "3개월":
        delta = timedelta(days=90)
    else:
        delta = timedelta(days=365)

    target_start = now - delta
    compare_start = target_start - delta

    # DB 연결
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    # 최근 기간 평점 데이터
    recent_data = session.query(
        Review.place_id, Review.star_rating, Review.registered_at
    ).filter(
        Review.registered_at >= target_start,
        Review.registered_at <= now
    ).all()

    # 이전 기간 평점 데이터
    prev_data = session.query(
        Review.place_id, Review.star_rating, Review.registered_at
    ).filter(
        Review.registered_at >= compare_start,
        Review.registered_at < target_start
    ).all()

    # 최근 감정 분석
    recent_sentiment = session.query(
        ReviewAnalysis.place_id, ReviewAnalysis.sentiment
    ).filter(
        ReviewAnalysis.created_at >= target_start,
        ReviewAnalysis.created_at <= now
    ).all()

    # 이전 감정 분석
    prev_sentiment = session.query(
        ReviewAnalysis.place_id, ReviewAnalysis.sentiment
    ).filter(
        ReviewAnalysis.created_at >= compare_start,
        ReviewAnalysis.created_at < target_start
    ).all()

    # 음식점 이름 매핑
    restaurant_map = dict(session.query(Restaurant.place_id, Restaurant.name).all())
    session.close()

    # 평점 처리
    recent_df = pd.DataFrame(recent_data, columns=["place_id", "star_rating", "date"])
    prev_df = pd.DataFrame(prev_data, columns=["place_id", "star_rating", "date"])

    recent_rating_avg = recent_df.groupby("place_id")["star_rating"].mean()
    prev_rating_avg = prev_df.groupby("place_id")["star_rating"].mean()

    rating_diff = (recent_rating_avg - prev_rating_avg).dropna().sort_values(ascending=False)

    # 감정 처리
    def positive_ratio(sentiments):
        if sentiments.empty:
            return 0
        return (sentiments == "긍정").sum() / len(sentiments)

    # DataFrame 변환
    recent_senti_df = pd.DataFrame(recent_sentiment, columns=["place_id", "sentiment"])
    prev_senti_df = pd.DataFrame(prev_sentiment, columns=["place_id", "sentiment"])

    # 긍정 비율 계산
    recent_pos = recent_senti_df.groupby("place_id")["sentiment"].apply(positive_ratio)
    prev_pos = prev_senti_df.groupby("place_id")["sentiment"].apply(positive_ratio)

    # 차이 계산
    senti_diff = recent_pos.subtract(prev_pos, fill_value=0).dropna().sort_values(ascending=False)

    # 평점 상승 Top10
    st.subheader(" 평점 상승 Top10")
    top10_rating = rating_diff.head(10).reset_index()
    top10_rating.columns = ["place_id", "rating_diff"]
    top10_rating["restaurant_name"] = top10_rating["place_id"].map(restaurant_map)

    st.dataframe(top10_rating[["restaurant_name", "rating_diff"]], use_container_width=True)

    # 긍정비율 상승 Top10
    st.subheader(" 긍정비율 상승 Top10")
    top10_senti = senti_diff.head(10).reset_index()
    top10_senti.columns = ["place_id", "positive_diff"]
    top10_senti["restaurant_name"] = top10_senti["place_id"].map(restaurant_map)

    st.dataframe(top10_senti[["restaurant_name", "positive_diff"]], use_container_width=True)

    # Altair 시각화
    st.subheader(" 평점 & 감정 급상승 분포 (시각화)")
    merged = pd.merge(top10_rating, top10_senti, on="place_id", how="outer")
    merged["restaurant_name"] = merged["restaurant_name_x"].fillna(merged["restaurant_name_y"])
    merged = merged.fillna(0)

    chart = alt.Chart(merged).mark_circle(size=100).encode(
        x=alt.X("rating_diff:Q", title="평점 상승량"),
        y=alt.Y("positive_diff:Q", title="긍정 비율 상승량"),
        color=alt.value("steelblue"),
        tooltip=["restaurant_name", "rating_diff", "positive_diff"]
    ).properties(
        width=700,
        height=400
    )

    st.altair_chart(chart, use_container_width=True)




elif menu == "6. 신뢰도 분석":
    st.header(" 리뷰 수 대비 평점 신뢰도 분석")

    st.markdown("""
    - 리뷰 수가 적은 경우 평점이 왜곡될 수 있으므로, **리뷰 수와 평점의 관계를 시각화**합니다.
    - 신뢰도는 리뷰 수 기준으로 5단계로 나누어 색상으로 구분합니다.
    """)

    # 리뷰 수 5개 이상만 필터링
    df_filtered = df[df["rating_count"] >= 5].copy()

    # 신뢰도 등급 추가
    df_filtered["신뢰도등급"] = pd.cut(
        df_filtered["rating_count"],
        bins=[0, 20, 100, 300, 800, float("inf")],
        labels=["매우낮음", "낮음", "보통", "높음", "매우높음"]
    )

    # 시각화 (Altair 점그래프)
    st.subheader(" 리뷰 수 vs 평점 (신뢰도 색상)")
    chart = alt.Chart(df_filtered).mark_circle(opacity=0.7).encode(
        x=alt.X("rating_count:Q", title="리뷰 수 (로그 스케일)", scale=alt.Scale(type='log')),
        y=alt.Y("rating_average:Q", title="평균 평점"),
        color=alt.Color("신뢰도등급:N", scale=alt.Scale(scheme='blues'), legend=alt.Legend(title="신뢰도등급")),
        size=alt.Size("positive_ratio:Q", title="긍정 비율", scale=alt.Scale(domain=[0, 1], range=[30, 300])),
        tooltip=["restaurant_name", "rating_count", "rating_average", "positive_ratio", "신뢰도등급"]
    ).properties(width=800, height=500)

    st.altair_chart(chart, use_container_width=True)

    st.markdown("---")

    # 상위 음식점 표 표시
    st.subheader(" 리뷰 수 많고 평점 높은 음식점 Top10")
    top10 = df_filtered.sort_values(by=["rating_count", "rating_average"], ascending=[False, False]).head(10)

    st.dataframe(top10[[ 
        "restaurant_name",
        "address",
        "rating_average",
        "rating_count",
        "positive_ratio",
        "신뢰도등급"
    ]].rename(columns={
        "restaurant_name": "음식점명",
        "address": "주소",
        "rating_average": "평균 평점",
        "rating_count": "리뷰 수",
        "positive_ratio": "긍정 비율"
    }), use_container_width=True)




elif menu == "7. 주인장의 음식점 추천":
    st.header(" GPT 기반 맛집 추천")
    st.markdown("""
    - 최근 핫하게 뜨고 있지만 아직 많이 알려지지 않은,  
    - 그래서 **'나만 아는 숨은 맛집'**처럼 느껴지는 곳을 추천해드립니다.
    """)

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    today = datetime.now()
    last_month = today - timedelta(days=30)

    engine = get_engine()
    Session = sessionmaker(bind=engine)
    session = Session()

    # 최근 한 달 리뷰 데이터
    recent_reviews = session.query(
        Review.place_id, Review.star_rating, Review.registered_at
    ).filter(
        Review.registered_at >= last_month
    ).all()

    review_df = pd.DataFrame(recent_reviews, columns=["place_id", "star_rating", "registered_at"])

    if review_df.empty:
        st.warning("최근 한 달간 리뷰가 부족하여 추천할 데이터가 없습니다.")
    else:
        recent_avg = review_df.groupby("place_id")["star_rating"].mean().rename("recent_avg_rating")
        recent_count = review_df.groupby("place_id").size().rename("recent_review_count")

        df = load_place_summary_with_location()

        merged = df.merge(recent_avg, on="place_id").merge(recent_count, on="place_id")

        candidate_df = merged[
            (merged["recent_avg_rating"] >= 4.3) &
            (merged["positive_ratio"] >= 0.75) &
            (merged["rating_count"] < 100)
        ]

        if candidate_df.empty:
            st.warning("조건에 맞는 음식점이 없습니다.")
        else:
            #  GPT에 넘길 프롬프트 구성 (place_id 포함)
            candidate_preview = candidate_df[[ 
                "place_id", "restaurant_name", "address", 
                "recent_avg_rating", "positive_ratio", "top_keywords"
            ]].head(20)

            prompt = f"""
다음은 최근 한 달간 평점이 높고 긍정 비율도 높지만,
아직 리뷰 수가 많지 않은 음식점 목록입니다.

이 중에서 "요즘 뜨고 있는 숨은 맛집" 같은 느낌으로
사람들에게 추천하고 싶은 Top 5를 골라주세요.
추천 이유도 한 줄씩 적어주세요.

음식점 목록:
{candidate_preview.to_string(index=False)}

결과 형식:
1. place_id: [숫자] - 추천 이유 한 줄
예시:
1. place_id: 12345 - 음식이 맛있고 분위기가 좋다는 리뷰가 많아요.
"""

            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )

                gpt_result = response.choices[0].message.content

                #  place_id 파싱
                import re
                place_ids = re.findall(r"place_id\s*:\s*(\d+)", gpt_result)
                place_ids = list(map(str, place_ids))
                candidate_df["place_id"] = candidate_df["place_id"].astype(str)

                # 추천 이유 깔끔하게 출력 (restaurant_name으로 대체)
                st.subheader("💡 GPT 추천 결과")

                lines = gpt_result.strip().split("\n")
                display_lines = []

                for line in lines:
                    match = re.match(r"\d+\.\s*place_id\s*:\s*(\d+)\s*-\s*(.*)", line.strip())
                    if match:
                        pid, reason = match.groups()
                        row = candidate_df[candidate_df["place_id"] == pid]
                        if not row.empty:
                            name = row.iloc[0]["restaurant_name"]
                            display_lines.append(f"- **{name}**: {reason.strip()}")

                if display_lines:
                    st.markdown("\n".join(display_lines))
                else:
                    st.info("GPT 응답에서 추천 내용을 추출할 수 없습니다.")

                #  음식점 상세 정보 표 출력
                if place_ids:
                    info_df = candidate_df[candidate_df["place_id"].isin(place_ids)]
                    st.subheader(" 추천 음식점 정보")
                    st.dataframe(
                        info_df[[
                            "restaurant_name", "address", "recent_avg_rating",
                            "positive_ratio", "rating_count", "top_keywords"
                        ]],
                        use_container_width=True
                    )
                else:
                    st.info("GPT 응답에서 place_id를 찾을 수 없습니다.")

            except Exception as e:
                st.error(f"GPT 추천 중 오류 발생: {e}")

    session.close()




