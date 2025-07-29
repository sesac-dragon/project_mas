#!/bin/bash
# 리눅스에서 이걸 통해 bash로 실행하겠다는 의미 없으면 안됨

# 0.테이블 생성(최초 1회만)
python /app/common/__init__.py

# 매 1시간마다 1000개 리뷰 감성 분석 실행 하고, 요약분석도 db에 저장함
echo "0 * * * * /usr/local/bin/python /app/analyzer/analyze_reviews.py && /usr/local/bin/python /app/analyzer/analyze_summary.py >> /app/analyzer/analyzer.log 2>&1" | crontab -


# 크론 데몬 실행 (컨테이너 유지)
cron -f
