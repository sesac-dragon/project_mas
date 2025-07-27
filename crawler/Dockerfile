# 1. Python 3.10 기반 이미지 사용
FROM python:3.10-slim

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. 로컬 코드 복사 (현재 dockerfile 있는 폴더 기준)
COPY . /app/

# 4. 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt
