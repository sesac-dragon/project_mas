from sqlalchemy.orm import sessionmaker
from common.db_connection import get_engine
from common.db_table import PlaceSummary, Restaurant
import pandas as pd
import sys
sys.path.append('/app') #crontab에서 경로를 못찾아서 /app 경로를 python 경로에 추가

from dotenv import load_dotenv
load_dotenv(dotenv_path="/app/.env")#crontab때문에 명시적으로 .env 파일 경로 지정

def load_place_summary_with_location():
  engine = get_engine()
  Session = sessionmaker(bind=engine)
  session = Session()

  try:
    results = session.query(
      PlaceSummary.place_id,
      PlaceSummary.positive,
      PlaceSummary.negative,
      PlaceSummary.neutral,
      PlaceSummary.total,
      PlaceSummary.positive_ratio,
      PlaceSummary.top_keywords,
      PlaceSummary.updated_at,
      Restaurant.name.label('restaurant_name'),
      Restaurant.address,
      Restaurant.lat,
      Restaurant.lon,
      Restaurant.rating_average,
      Restaurant.rating_count
    ).join(Restaurant,PlaceSummary.place_id == Restaurant.place_id).all()

    df = pd.DataFrame([r._asdict() for r in results])
    return df
  finally:
    session.close()