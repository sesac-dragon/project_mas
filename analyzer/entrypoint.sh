#!/bin/bash
# 리눅스에서 이걸 통해 bash로 실행하겠다는 의미 없으면 안됨

# 매 2시간마다 1000개 리뷰 감성 분석 실행
echo "0 */2 * * * /usr/local/bin/python /app/analyzer/analyze_reviews.py >> /app/analyzer/analyzer.log 2>&1" > /etc/cron.d/analyze-cron


# 크론 권한 설정
chmod 0644 /etc/cron.d/analyze-cron

# 크론 데몬 실행 (컨테이너 유지)
cron -f
