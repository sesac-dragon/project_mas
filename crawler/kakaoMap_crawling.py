import requests
import json
import time
import re
import pandas as pd
from sqlalchemy import create_engine #db 연결을 위해
from sqlalchemy.exc import IntegrityError # 중복 리뷰를 처리하기 위해
from strength_enum import StrengthEnum # 강점 ids를 맵핑하기 위해 enum 클래스 생성하여 import 했음



#음식점 크롤링 하는 메서드
#theme_id -테마 코드 ( 현재는 음식점 고정이나, 나중에 확장을 할수도 있어서 따로 파라미터로 뺌)
#rect- 지도 범위
def get_kakao_restaurants(theme_id,rect,max_page=50):
  all_places = []
  for cpage in range(1, max_page + 1 ):
    url = 'https://search.map.kakao.com/mapsearch/theme.daum'

    params = {
      'output':'json',
      'category':'y',
      'callback':'jQuery18109872917320938157_1753103241831',
      'theme_id':theme_id,
      'cpage':cpage,
      'rect':rect
    }

    headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36','referer':'https://map.kakao.com/'}

    jsonp = requests.get(url,params=params,headers=headers)
    if jsonp.status_code != 200:
      print(f'{cpage}페이지에서 에러가 발생했습니다.')
      break
    #앞에거 다 빼고 jQuery로 시작되는 부분부터 안에꺼 가져오기.
    res = re.search(r'jQuery\d+_\d+\((.*)\)', jsonp.text)

    if not res:
      print(f'{cpage}페이지에서 json 파싱 실패')
      continue

    #group(0) : 정규식 전체와 매치된 부분
    #group(1) : 첫 번째 소괄호 ( ... )에 해당하는 부분
    json_data = json.loads(res.group(1))

    places = json_data.get('place',[])

    if not places:
      break
    for p in places:
      all_places.append({
        'place_id':p['confirmid'],
        'name':p['name'],
        'address':p.get('address',''),
        'new_address':p.get('new_address',''),
        'lon':p.get('lon'),
        'lat':p.get('lat'),
        'tel':p.get('tel'),
        'category_depth1':p.get('cate_name_depth1'),
        'category_depth2':p.get('cate_name_depth2'),
        'category_depth3':p.get('cate_name_depth3'),
        'category_depth4':p.get('cate_name_depth4'),
        'category_depth5':p.get('cate_name_depth5'),
        'rating_average':p.get('rating_average',0.0),
        'rating_count':p.get('rating_count',0),
        'img':p.get('img')
      })
    print(f'capage={cpage} ({len(all_places)}개 누적)')
    time.sleep(0.2)
  return pd.DataFrame(all_places)





#리뷰 크로링하는 메서드
def get_kakao_reviews(place_id, limit=10 ,max_page=100):

  all_reviews = []
  previous_last_review_id = None
  page = 1
  strength_maping = {}

  while True:
    url = f'https://place-api.map.kakao.com/places/tab/reviews/kakaomap/{place_id}'

    params = {
      'order':'RECOMMENDED',
      'only_photo_review':'false',
      'page': page,
      'limit':limit
      }
    
    if previous_last_review_id:
      params['previous_last_review_id'] = previous_last_review_id
    
    header = {
      'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        'referer':'https://map.kakao.com/',
        'origin':'https://place.map.kakao.com',
        'pf':'web',
        'priority':'u=1, i',
        'referer':'https://place.map.kakao.com/'
    }

    resp = requests.get(url,params=params,headers=header)

    if resp.status_code !=200:
      print(f'Error {resp.status_code} at page {page}에서 에러가 났습니다.' )
      break
    data = resp.json()

    reviews = data.get('reviews',[])

    if not reviews:
      break

    for r in reviews:
      all_reviews.append({
        'review_id':r['review_id'],
        'star_rating':r['star_rating'],
        'contents':r.get('contents',''), # r에 'contents' key가 없으면 빈 문자열 '' 반환(default 생략하면 None)
        'registered_at':r.get('registered_at'),
        'updated_at':r.get('updated_at'),
        'strength':[StrengthEnum.get_strength_by_id(i) for i in r.get('strength_ids', [])] #enum 클래스를 가져와서 맵핑함
      })

    if not data.get('has_next',False):
      break

    previous_last_review_id = reviews[-1]['review_id'] #마지막 리뷰의 id로 업데이트
    page += 1

    if page > max_page:
      break
    time.sleep(0.5)
  return pd.DataFrame(all_reviews)


#해당 지역 음식점을 4등분 하기
def split_rect_into_4(rect):
  x1,y1,x2,y2 = map(int,rect.split(','))
  xm = (x1 + x2)  // 2
  ym = (y1 + y2)  // 2

  return [
    f'{x1},{y1},{xm},{ym}', #좌하
    f'{xm},{y1},{x2},{ym}', #우하
    f'{x1},{ym},{xm},{y2}', #좌상
    f'{xm},{ym},{x2},{y2}', #우상
  ]



def full_crawling(full_rect,theme_id='c9'):

  #데이터 베이스 연결 
  user = 'root'
  password = 'test1234'
  host = 'localhost'
  port = 3306
  db = 'local_kakao_placeDB'
  engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4')

  # 지역 4등분
  rects = split_rect_into_4(full_rect)
  all_places = []

  for i , rect in enumerate(rects):
    print(f'\n [rect {i +1 }/4] 범위: {rect}')
    #1/4 지역의 음식점 데이터 저장
    partial_place = get_kakao_restaurants('c9',rect,max_page=50)
    print(f'{len(partial_place)}개 크롤링 완료')
    all_places.append(partial_place)
    time.sleep(1) 

  #병합
  df_places = pd.concat(all_places, ignore_index=True)
  #중복제거
  df_places.drop_duplicates(subset='place_id',inplace=True)

  #DB 저장
  try:
    df_places.to_sql('restaurants', engine, if_exists='append', index=False)
  except IntegrityError as e1:
    print(f"음식점 중복 리뷰 무시  {e1}")

  
  # 리뷰데이터 저장
  for i , p_id in enumerate (df_places['place_id']): # 몇번째 음식점 처리중인지 확인을 위해 enumerate를 씀
    try:
      df_reviews = get_kakao_reviews(p_id,limit=20)
      if df_reviews.empty:
        print(f'{p_id}에 대한 리뷰 없음')
        continue

      df_reviews['place_id'] = p_id
      #리스트를 문자열로 , 로 구분해서넣음
      df_reviews['strength'] = df_reviews['strength'].apply(lambda x: ','.join(x)) 

      try:
        df_reviews.to_sql('reviews',engine,if_exists='append',index=False)
      except IntegrityError as e2:
        print(f'리뷰 중복 리뷰 무시 {e2}')
        continue
      print(f'[{i + 1}/{len(df_places)}] {p_id} - 리뷰 {len(df_reviews)}개 저장 완료')
      time.sleep(0.5)

    except Exception as e:
      print(f'{p_id} 처리 중 오류 발생: {e}')
      continue

  


