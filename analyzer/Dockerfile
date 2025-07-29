# 1. Python 3.10 기반 이미지 사용
FROM python:3.10-slim

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. PYTHONPATH 등록
ENV PYTHONPATH=/app

# 3-1. 시간대 설정 (KST 고정)
ENV TZ=Asia/Seoul

RUN apt-get update && apt-get install -y cron tzdata && \
    ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone

# 4. 공통 코드 복사
COPY common ./common

# 5. analyzer 코드 복사
COPY analyzer ./analyzer

# 6. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. 엔트리포인트 실행 권한 부여
RUN chmod +x /app/analyzer/entrypoint.sh

# 8. 크론 실행
CMD ["/app/analyzer/entrypoint.sh"]