from sqlalchemy.orm import sessionmaker
from common.db_connection import get_engine
from common.db_table import ReviewAnalysis, Base
from collections import Counter
from sqlalchemy import func
from common.db_table import PlaceSummary
from datetime import datetime
import pandas as pd
import pytz


def summarize_analysis():

  #DB 연결
  engine = get_engine()
  Base.metadata.create_all(engine) #테이블 없을 경우 자동 생성
  Session = sessionmaker(bind=engine)
  session = Session()

  # 감성 분석 결과 전체 조회
  analysis_data = session.query(ReviewAnalysis).all()

  # Dataframe 출력
  df = pd.DataFrame([{
    'place_id': r.place_id,
    'sentiment': r.sentiment,
    'keywords': r.keywords
  }for r in analysis_data])

  # 감정별 리뷰 갯수 집계
  sentiment_summary = df.groupby(['place_id', 'sentiment']).size().unstack(fill_value=0).reset_index()

  # 특정 음식점(place_id)에 어떤 감정이 한 번도 안 나온 경우, unstack() 결과에서 해당 감정 컬럼이 누락될 수 있음
  #그래서 없는 감정 컬럼이 있다면 추가해야한다.
  for sentiment in ['긍정', '부정' , '중립']:
    if sentiment not in sentiment_summary.columns:
      sentiment_summary[sentiment] = 0


  sentiment_summary['total'] = sentiment_summary[['긍정','부정','중립']].sum(axis=1)
  sentiment_summary['긍정비율'] = (sentiment_summary['긍정'] / sentiment_summary['total'] * 100).round(2)

  #키워드 정리
  def extract_keywords(group):
    keyword_list = []
    for k in group['keywords']:
      keyword_list.extend([kw.strip() for kw in k.split(',') if kw.strip()])
    top_keywords = [kw for kw, _ in Counter(keyword_list).most_common(5)]
    return ",".join(top_keywords)

  keywords_summary = df.groupby('place_id').apply(extract_keywords).reset_index(name="대표 키워드")

  #감정분석과 키워드 데이터 병합
  summary = pd.merge(sentiment_summary,keywords_summary, on='place_id')
  
  return summary

def save_summary(summary_df):
  engine = get_engine()
  Session = sessionmaker(bind=engine)
  session = Session()
  KST = pytz.timezone("Asia/Seoul")

  try:
    for _, row in summary_df.iterrows():
      summary = PlaceSummary(
        place_id = row['place_id'],
        positive=int(row['긍정']),
        negative=int(row['부정']),
        neutral=int(row['중립']),
        total=int(row['total']),
        positive_ratio=float(row['긍정비율']),
        top_keywords=row['대표 키워드'],
        updated_at=datetime.now(KST)
      )
      session.merge(summary)
    session.commit()
    print(f"[저장완료] {len(summary_df)}개 저장됨")
  except Exception as e:
    session.rollback()
    print((f"[저장실패] {e}"))
  finally:
    session.close()



if __name__ == "__main__":
  summary_df = summarize_analysis()
  print(summary_df.head())
  save_summary(summary_df)

