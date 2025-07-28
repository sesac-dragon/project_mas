import time
import pymysql
from kakaoMap_crawling import full_crawling
import os
from common.db_connection import get_engine
from common.db_table import Base

#컨테이너에서 DB가 준비 될 시간을 기다리기 위해
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
      print(f"DB 연결 대기 중 ...({i+1}/30) - host {os.getenv('DB_HOST')}")
      time.sleep(3)
  raise Exception("DB에 연결할 수 없습니다.")

if __name__ == "__main__":
  wait_for_mysql()
  engine = get_engine()

  # DB에 테이블이 없을 경우 자동 생성
  Base.metadata.create_all(engine)

  # 전체 사각형 범위 설정
  full_rect = '487005,1116407,493715,1122797'
  full_crawling(full_rect,engine)