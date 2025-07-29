import time
import pymysql
from kakaoMap_crawling import full_crawling
from common.db_connection import get_engine
from common.db_table import Base
from dotenv import load_dotenv
import os,sys
sys.path.append('/app') #crontab에서 경로를 못찾아서 /app 경로를 python 경로에 추가
load_dotenv(dotenv_path="/app/.env")



if __name__ == "__main__":
  engine = get_engine()

  # DB에 테이블이 없을 경우 자동 생성
  Base.metadata.create_all(engine)

  # 전체 사각형 범위 설정
  full_rect = '487005,1116407,493715,1122797'
  full_crawling(full_rect,engine)