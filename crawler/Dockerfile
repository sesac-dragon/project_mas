# 1. Python 3.10 기반 이미지 사용
FROM python:3.10-slim

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. 모듈 검색 경로(PYTHON PATH)에 /app을 추가
ENV PYTHONPATH=/app

# 3-1. 시간대를 KST로 고정(cron은 시스템 시간 기준)
ENV TZ=Asia/Seoul
RUN apt-get update && apt-get install -y cron tzdata && \
    ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime && \
    echo "Asia/Seoul" > /etc/timezone

# 4. 공통 코드 복사
COPY common ./common

# 5. 로컬 코드 복사 (현재 context를 잡고 있는 폴더 기준)
COPY crawler ./crawler

# 6. 의존성 파일 카피
COPY requirements.txt .

# 7. 의존성 설치
RUN pip install -r requirements.txt

# 8. 자동화 파일 실행 권한 부여
RUN chmod +x /app/crawler/entrypoint.sh

# 크론탭 실행
CMD ["/app/crawler/entrypoint.sh"]
