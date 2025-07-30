# 1. Python 3.10 기반 이미지 사용
FROM python:3.10

# 2. 작업 디렉토리 생성
WORKDIR /app

# 3. PYTHONPATH 설정
ENV PYTHONPATH=/app

# 4. 시간대 KST 고정 및 워드클라우드 한글폰트(Nanum) 설치
ENV TZ=Asia/Seoul
RUN apt-get update && apt-get install -y \
    tzdata \
    fonts-nanum \
    && ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime \
    && echo "Asia/Seoul" > /etc/timezone \
    && fc-cache -fv \
    && apt-get clean

# 5. 공통 코드 복사
COPY common ./common

# 6. .env 복사
COPY .env /app/.env

# 7. visualize 폴더 복사
COPY visualize ./visualize

# 8. requirements 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 9. Streamlit 앱 실행
CMD ["streamlit", "run", "visualize/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
