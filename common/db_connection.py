import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

def get_engine():
  DB_USER = os.getenv("DB_USER")
  DB_PASSWORD = os.getenv("USER_PASSWORD")
  DB_HOST = os.getenv("DB_HOST") 
  DB_PORT = os.getenv("DB_PORT")
  DB_NAME = os.getenv("DATABASE")

  url = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
  return create_engine(url)