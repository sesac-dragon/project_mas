# 1. Python 3.10 기반 이미지 사용
FROM python:3.10-slim

# 2. 작업 디렉토리 생성
WORKDIR /app

# 공통 코드 복사
COPY common ./common

# analyzer 코드 복사(현재 context를 잡고 있는 폴더 기준)
COPY analyzer ./analyzer

# 필수 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt