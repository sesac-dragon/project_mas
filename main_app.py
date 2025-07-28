import subprocess
import datetime
import os



def run_crawler():
  print(f"[{datetime.datetime.now()}] 크롤러 자동 실행 시작")

  # 크롤링 시작
  #stdout(표준 출력)과 stderr(표준 에러 출력)을 캡처
  #result.stdout, result.stderr에서 확인 가능
  #캡처된 출력을 바이트가 아니라 문자열(str)로 받음
  #여기서 result는 CompletedProcess 객체를 반환- returncode , stdout,stderr 메서드를 반환함
  result = subprocess.run(
    ["python3", "crawler/crawling_app.py"],
    capture_output=True, 
    text=True
  )

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


