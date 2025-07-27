import time
import pymysql
from kakaoMap_crawling import full_crawling
from db_table import Base
from sqlalchemy import create_engine
import os

def wait_for_mysql():
  for i in range(30):
    try:
      conn = pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("USER_PASSWORD"),
        port=int(os.getenv("DB_PORT")),
        )
      conn.close()
      print("DB 연결성공")
      return
    except Exception as e:
      print(f"DB 연결 대기 중 ...({i+1}/30)")
      time.sleep(3)
  raise Exception("DB에 연결할 수 없습니다.")

wait_for_mysql() # 함수 호출


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("USER_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DATABASE")

url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

engine = create_engine(url)

# DB에 테이블이 없을 경우 자동 생성
Base.metadata.create_all(engine)

full_rect = '487005,1116407,493715,1122797'
full_crawling(full_rect,engine)