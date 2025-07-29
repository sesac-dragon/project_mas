# 1. Python 3.10 기반 이미지 사용
FROM python:3.10

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. PYTHONPATH 등록
ENV PYTHONPATH=/app

# 3-1. 시간대 설정 (KST 고정)
ENV TZ=Asia/Seoul

#4. 필요한 패키지 설치
RUN apt-get update && apt-get install -y cron tzdata && \
    ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone

# 4. 공통 파이썬 코드 복사
COPY common ./common
# .env 파일 복사
COPY .env /app/.env


# 5. analyzer 코드 복사
COPY analyzer ./analyzer

# 6. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 7. 엔트리포인트 실행 권한 부여
RUN chmod +x /app/analyzer/entrypoint.sh

# 7-1. 크론용 쉘스크립트 복사 및 실행 권한 부여
RUN chmod +x /app/analyzer/cron_runner.sh


# 8. 크론 실행
CMD ["/app/analyzer/entrypoint.sh"]
