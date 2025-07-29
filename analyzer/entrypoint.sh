#!/bin/bash
# 리눅스에서 이걸 통해 bash로 실행하겠다는 의미 없으면 안됨

echo "ENTRYPOINT 시작"

echo "ENTRYPOINT 시작"

# 0. .env 로드 (.env 파일이 /app/.env 위치에 있어야 함)
if [ -f /app/.env ]; then
  export $(cat /app/.env | grep -v '^#' | xargs)
  echo ".env 환경변수 로드 완료"
else
  echo "/app/.env 파일이 존재하지 않습니다"
fi

# 1. DB 연결 대기
echo "DB 연결 대기 중..."
until python -c "
import os, pymysql
try:
  pymysql.connect(
    host=os.getenv('DB_HOST'),
    port=int(os.getenv('DB_PORT', 3306)),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME')
  )
except Exception as e:
  print(f' 연결 실패: {e}')
  raise
"; do
  sleep 1
done
echo "DB 연결 성공!"

# 0.테이블 생성(최초 1회만)
python /app/common/__init__.py

echo "크론탭 등록 중..."


# 매 1시간마다 1000개 리뷰 감성 분석 실행 하고, 요약분석도 db에 저장함
echo "0 * * * * PYTHONPATH=/app /usr/local/bin/python /app/analyzer/analyze_reviews.py >> /app/analyzer/analyzer.log 2>&1" > /tmp/cronjob
echo "5 * * * * PYTHONPATH=/app /usr/local/bin/python /app/analyzer/analyze_summary.py >> /app/analyzer/analyzer.log 2>&1" >> /tmp/cronjob
crontab /tmp/cronjob
rm /tmp/cronjob

echo "크론 시작"
cron -f
