#!/bin/bash
# 리눅스에서 이걸 통해 bash로 실행하겠다는 의미 없으면 안됨


# 0. .env 로드 (.env 파일이 /app/.env 위치에 있어야 함)
if [ -f /app/.env ]; then
  export $(grep -v '^#' /app/.env | xargs)
  echo ".env 환경변수 로드 완료"
else
  echo "/app/.env 파일이 존재하지 않습니다"
fi

# 1. DB 연결 대기
echo "DB 연결 대기 중..."
until python -c "
import os, pymysql
host = os.getenv('DB_HOST')
port = int(os.getenv('DB_PORT', 3306))
user = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
database = os.getenv('DB_NAME')
conn = pymysql.connect(host=host, port=port, user=user, password=password, database=database)
conn.close()
"; do
  echo "연결 실패... 재시도 중"
  sleep 1
done
echo "DB 연결 성공!"

# 0.테이블 생성(최초 1회만)
python /app/common/__init__.py

# 크론탭 설정: 매일 오전 2시 실행
echo "0 2 * * * PYTHONPATH=/app /usr/local/bin/python /app/crawler/crawling_app.py >> /app/crawler/crawler.log 2>&1" | crontab -

# 크론 실행
cron -f
