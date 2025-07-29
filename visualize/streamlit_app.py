import streamlit as st
import pandas as pd
from total_map_data import load_place_summary_with_location
from wordcloud import WordCloud
import matplotlib.pyplot as plt

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
menu = st.sidebar.radio("메뉴 선택"), [
  "1. 평점 기반 통계",
  "2. 감성 분석 요약",
  "3. 리뷰 키워드 분석",
  "4. 지도 기반 시각화",
  "5. 시간 흐름 분석",
  "6. 신뢰도 분석",
  "7. 음식점 추천"
]


if menu == "1. 평점 기반 통계":
    st.header("⭐ 평점 기반 음식점 Top 10")
    
    top10 = df.sort_values(by="rating_average", ascending=False).head(10)

    st.bar_chart(
        data=top10.set_index("restaurant_name")["rating_average"],
        use_container_width=True
    )

    st.markdown("가장 평점이 높은 음식점 상위 10개를 바 차트로 시각화한 결과입니다.")

    st.header("😢 평점 낮은 음식점 Bottom 10")

    bottom10 = df[df["rating_average"] > 0].sort_values(by="rating_average", ascending=True).head(10)

    st.bar_chart(
        data=bottom10.set_index("restaurant_name")["rating_average"],
        use_container_width=True
    )

    st.markdown("평점이 가장 낮은 음식점 10곳입니다.")

    st.header("📊 전체 평점 분포 히스토그램")

    st.histogram_chart(df["rating_average"])

elif menu == "2. 감성 분석 요약":
   st.header("💚 긍정 비율 Top 10 음식점")
   top10_pos = df.sort_values(by="positive_ratio", ascending=False).head(10)

   st.bar_chart(top10_pos.set_index("restaurant_name")["positive_ratio"])

   st.subheader("☁️ 해당 음식점들의 대표 키워드 워드클라우드")

  

   keyword_text = ", ".join(top10_pos["top_keywords"].dropna().tolist())
   wordcloud = WordCloud(
      font_path="/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
      width=800, height=400, background_color="white"
   ).generate(keyword_text)

   fig, ax = plt.subplots()
   ax.imshow(wordcloud, interpolation='bilinear')
   ax.axis("off")
   st.pyplot(fig)

   st.caption("※ 상위 긍정 음식점들의 키워드를 바탕으로 생성된 워드클라우드입니다.")

   # ✅ Top10 음식점 상세 정보 표시
   st.subheader("📋 음식점 상세 정보")
   display_cols = ["restaurant_name", "address", "rating_average", "rating_count", "positive_ratio", "top_keywords"]
   display_df = top10_pos[display_cols].rename(columns={
      "restaurant_name": "이름",
      "address": "주소",
      "rating_average": "평균 평점",
      "rating_count": "리뷰 수",
      "positive_ratio": "긍정 비율",
      "top_keywords": "대표 키워드"
    })

   st.dataframe(display_df, use_container_width=True)
  

   st.divider()
   st.header("💔 긍정 비율 낮은 음식점 Top 10")

   # 리뷰 수가 어느 정도 있는 음식점 중에서만 보기 (예: 리뷰 10개 이상)
   bottom10_pos = df[df["total"] >= 10].sort_values(by="positive_ratio", ascending=True).head(10)

   st.bar_chart(bottom10_pos.set_index("restaurant_name")["positive_ratio"])
  
   st.subheader("☁️ 해당 음식점들의 대표 키워드 워드클라우드 (부정 Top10)")

   negative_keyword_text = ", ".join(bottom10_pos["top_keywords"].dropna().tolist())

   neg_wordcloud = WordCloud(
      font_path="/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
      width=800, height=400,
      background_color="white",
      colormap="Reds"  # 🔴 부정적인 느낌을 강조하는 색상
   ).generate(negative_keyword_text)

   fig2, ax2 = plt.subplots()
   ax2.imshow(neg_wordcloud, interpolation='bilinear')
   ax2.axis("off")
   st.pyplot(fig2)

   st.caption("※ 부정 평가를 많이 받은 음식점들의 키워드입니다.")

   st.subheader("📋 부정 평가 음식점 상세 정보")
   bottom_display = bottom10_pos[display_cols].rename(columns={
      "restaurant_name": "이름",
      "address": "주소",
      "rating_average": "평균 평점",
      "rating_count": "리뷰 수",
      "positive_ratio": "긍정 비율",
      "top_keywords": "대표 키워드"
   })

   st.dataframe(bottom_display, use_container_width=True)


elif menu == "3. 리뷰 키워드 분석":
    st.header("💬 리뷰 키워드 트렌드")
    st.write("키워드 빈도, 감정 키워드 변화, 급등 키워드 추이 등")

elif menu == "4. 지도 기반 시각화":
    st.header("🗺️ 지도 시각화")
    st.write("음식점 위치, 평점 색상 표시, 핫플레이스 클러스터링 등")

elif menu == "5. 시간 흐름 분석":
    st.header("📆 시간 흐름 분석")
    st.write("1개월/3개월/1년 기준 평점 및 감정 변화 추이")

elif menu == "6. 신뢰도 분석":
    st.header("🔎 리뷰 수 대비 평점 신뢰도")
    st.write("리뷰 수 vs 평점, 신뢰도 기반 색상 강조, 표준편차 시각화")

elif menu == "7. 음식점 추천":
    st.header("🔍 음식점 추천 시스템")
    st.write("사용자 조건 기반 추천: 평점, 키워드, 위치 기반 추천")