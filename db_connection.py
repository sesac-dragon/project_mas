import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

#도커 컴포즈로 실행하지 않을때는 DB_HOST 값 덮어쓰기
if os.getenv("RUN_ENV")== "host":
  os.environ["DB_HOST"] = "127.0.0.1"


def get_engine():
  DB_USER = os.getenv("DB_USER")
  DB_PASSWORD = os.getenv("USER_PASSWORD")
  DB_HOST = os.getenv("DB_HOST")  # 환경에 따라 달라짐
  DB_PORT = os.getenv("DB_PORT")
  DB_NAME = os.getenv("DATABASE")

  url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
  return create_engine(url)