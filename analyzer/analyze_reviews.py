from openai import OpenAI
from sqlalchemy.orm import sessionmaker
from common.db_connection import get_engine
from common.db_table import Review, ReviewAnalysis
from datetime import datetime
from dotenv import load_dotenv
import pytz,os,time,sys
sys.path.append('/app') 

load_dotenv(dotenv_path="/app/.env") #이게 있어도 위에 서 import할때 적용이 안되므로 이미 cron에서 실행할때 미리 지정되어야 한다.

client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

# DB 연결 
engine = get_engine()
Session = sessionmaker(bind=engine)


#gpt에 보낼 prompt 문자열을 구성
#ChatCompletion 생성 함수 (GPT와 대화하듯 요청)
#user가 나라고 생각하고, assistant가 gpt라 생각하면 될듯?
#temperature=0.7: 생성 결과의 창의성/무작위성 조절값(0.0에 가까울수록 정확하고 일관된 결과)
def analyze_sentiment(text):
  prompt = f"""
  리뷰 내용을 분석해줘.

  1. 리뷰의 감정을 '긍정', '부정', '중립' 중 하나로 정확히 분류해줘.  
    - 리뷰가 감정이 드러나지 않거나 판단이 어려운 경우에는 반드시 '중립'으로 해줘.

  2. 리뷰에서 핵심적인 감성 키워드 3개를 추출해줘.  
    - 키워드는 명사 또는 형용사 위주로, 감정을 표현하거나 특징을 나타내는 단어를 골라줘.  
    - 예: "맛있다", "친절", "가성비", "불친절", "위생" 등  
    - 단, 리뷰에 감정이나 특징을 판단할만한 정보가 거의 없을 경우, 키워드는 생략해도 돼 (빈 칸 허용).  
    - 키워드는 반드시 한국어로 출력해줘.


  예시 응답 형식: (반드시 이 포맷 그대로):

  감정 : 긍정
  키워드 : "친절", "가성비" , "맛있다"

  또는 감정이 불명확할 경우:

  감정 : 중립  
  키워드 :

  
  리뷰: "{text}"
  """
  try:
    response = client.chat.completions.create(
      model="gpt-4o",
      messages=[
        {"role": "user", "content": prompt}
      ],
      temperature=0.7
    )
    return response.choices[0].message.content.strip()
  except Exception as e:
    print(f"[API 에러] {e}")
    return None
  

def parse_response(response):
  try:
    lines = response.strip().split('\n')
    sentiment_line = next(line for line in lines if '감정' in line)
    keywords_line = next(line for line in lines if "키워드" in line)

    #제목은 버리고 내용만 가져옴
    sentiment = sentiment_line.split(":")[1].strip()
    keywords_raw = keywords_line.split(":")[1].strip()
    keywords = [kw.strip() for kw in keywords_raw.split(',') if kw.strip()]

    return sentiment, keywords
  except Exception as e:
    print(f"[파싱 에러] {e}")
    return None , None
  
def run_analysis(limit=1000):
  #트랜스미션 단위로 db접속 함.
  session = Session()
  try:
    # 이미 분석된 리뷰 제외하고 최대 1000개 가져오기
    subquery = session.query(ReviewAnalysis.review_id)
    #리뷰 테이블에서 데이터 조회해서/ filter는 조건문/ ~는 not 을 의미함/ .all()은 리스트형태로 반환함
    reviews = session.query(Review).filter(~Review.review_id.in_(subquery)).limit(limit).all()

    print(f"[INFO] {len(reviews)}건의 리뷰를 분석합니다.")
    for review in reviews:
      if not review.contents:
        print(f"[SKIP] 리뷰 {review.review_id}: 내용 없음")
        continue

      print(f"[분석 중] 리뷰 ID: {review.review_id}")
      response = analyze_sentiment(review.contents)
      if not response:
        print(f"[SKIP] 리뷰 {review.review_id}: GPT 응답 실패")
        continue

      sentiment, keywords = parse_response(response)
      if not sentiment :
        print(f"[SKIP] 리뷰 {review.review_id}: 감정 파싱 실패")
        continue
      
      time.sleep(1.2)



      KST = pytz.timezone("Asia/Seoul") #한국시간 설정을 위해

      analysis = ReviewAnalysis(
        review_id=review.review_id,
        place_id=review.place_id,
        sentiment=sentiment,
        keywords=", ".join(keywords),
        model_used="gpt-4o",
        created_at=datetime.now(KST)
      )

      try:
        session.add(analysis)
        session.commit()
        print(f"[저장 완료] 리뷰 {review.review_id}")
      except Exception as db_err:
        print(f"[DB 오류] 리뷰 {review.review_id}: {db_err}")
        session.rollback()

  finally:
    session.close()

if __name__ == "__main__":
  run_analysis(limit=1000)