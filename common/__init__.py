from db_connection import get_engine
from db_table import Base

def init():
  engine = get_engine()
  Base.metadata.create_all(engine)
  print("모든 테이블 생성 완료")

if __name__ == "__main__":
  init()