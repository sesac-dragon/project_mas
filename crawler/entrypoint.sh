#!/bin/bash
# 리눅스에서 이걸 통해 bash로 실행하겠다는 의미 없으면 안됨


# 크론탭 설정: 매일 오전 2시 실행
echo "0 2 * * * /usr/local/bin/python /app/crawler/crawling_app.py >> /app/crawler/crawler.log 2>&1" | crontab -

# 크론 실행
cron -f
