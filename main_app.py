import subprocess
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

def run_crawler():
  print(f"[{datetime.datetime.now()}] 크롤러 자동 실행 시작")

  # 크롤링 시작
  #여기서 result는 CompletedProcess 객체를 반환- returncode , stdout,stderr 메서드를 반환함
  result = subprocess.run(
    ["python3", "crawler/crawling_app.py"])

  #결과 출력
  if result.returncode == 0:
    print(f"[{datetime.datetime.now()}] 크롤러 실행 완료")
  else:
    print(f"[{datetime.datetime.now()}] 크롤러 실행 실패")
    print("stderr:\n", result.stderr)


if __name__ == "__main__":
  #어디서 이 파일을 실행하든 항상 main_app.py가 있는 폴더로 이동후 실행
  os.chdir(os.path.dirname(os.path.abspath(__file__))) 
  run_crawler()


