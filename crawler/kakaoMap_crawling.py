import requests
import json
import time
import re
import pandas as pd
from sqlalchemy import create_engine #db 연결을 위해
from sqlalchemy.exc import IntegrityError # 중복 리뷰를 처리하기 위해
from .strength_enum import StrengthEnum # 강점 ids를 맵핑하기 위해 enum 클래스 생성하여 import 했음



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


#해당 지역을 4등분 하는 메서드
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

# 해당 지역 음식점이 500개가 넘으면 4등분해서 500개 안넘을때까지 분할하면서 크롤링하는 메서드
def recursive_crawling(rect,theme_id='c9',depth=0,max_depth=4):
  df = get_kakao_restaurants(theme_id,rect,max_page=50)
  print(f'[depth={depth}] {rect} ->{len(df)}개 크롤링 완료')
  
  if len(df) >= 500 and depth < max_depth:
    print(f'데이터가 500개 초과되어 {rect} 세부 분할함')
    sub_rects = split_rect_into_4(rect)
    dfs =[]
    for sub in sub_rects:
      dfs.append(recursive_crawling(sub,theme_id,depth=depth+1,max_depth=max_depth))
    return pd.concat(dfs,ignore_index=True) #ignore_index= True 는 데이터프레임 합칠때 index를 0부터 새로 부여
  else:
    return df



#지도 구역데이터(full_rect)를 매개변수로 받아서 전체 크롤링하는 메서드
def full_crawling(full_rect,theme_id='c9'):

  #데이터 베이스 연결 
  user = 'root'
  password = 'test1234'
  host = 'localhost'
  port = 3306
  db = 'local_kakao_placeDB'
  engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4')

  #전체 지역을 재귀적으로 크롤링
  print(f'\n 전체 구역 {full_rect}에서 크롤링 시작')
  all_places = recursive_crawling(full_rect,theme_id=theme_id)

  #중복제거
  all_places.drop_duplicates(subset='place_id',inplace=True)

  #기존 DB 조회해서 중복되는 데이터 제외
  try:
    restaurant_list = pd.read_sql("SELECT place_id FROM restaurants",con=engine)
    place_id_list = set(restaurant_list['place_id'].astype(str)) #astype은 자료타입을 변환한다. 즉 str로 변환한다.
    all_places = all_places[~all_places['place_id'].astype(str).isin(place_id_list)]# ~는 not을 의미한다. 
    print(f'신규 음식점 {len(all_places)}개만 필터링 완료')
  except Exception as e :
    print(f'기존 음식점 조회 실패: {e}')
    place_id_list = set()


  #DB 저장
  if not all_places.empty:
    try:
      all_places.to_sql('restaurants', engine, if_exists='append', index=False)
    except IntegrityError as e1:
      print(f"음식점 중복 리뷰 무시  {e1}")

  
  # 리뷰데이터 저장
  for i , p_id in enumerate (all_places['place_id']): # 몇번째 음식점 처리중인지 확인을 위해 enumerate를 씀
    try:
      df_reviews = get_kakao_reviews(p_id,limit=20)

      if df_reviews.empty:
        print(f'{p_id}에 대한 리뷰 없음')
        continue

      try:
        review_list = pd.read_sql(f"SELECT review_id FROM reviews WHERE place_id = '{p_id}'",con=engine)
        review_ids = set(review_list['review_id'].astype(str))
        df_reviews = df_reviews[~df_reviews['review_id'].astype(str).isin(review_ids)]
      except Exception as e:
        print(f'기존 리뷰 조회 실패(전체 저장): {e}')
      if df_reviews.empty:
        print(f'{p_id}의 리뷰는 모두 이미 있음')
        continue

      df_reviews['place_id'] = p_id
      #리스트를 문자열로 , 로 구분해서넣음
      df_reviews['strength'] = df_reviews['strength'].apply(lambda x: ','.join(x)) 

      try:
        df_reviews.to_sql('reviews',engine,if_exists='append',index=False)
      except IntegrityError as e2:
        print(f'리뷰 중복 리뷰 무시 {e2}')
        continue
      print(f'[{i + 1}/{len(all_places)}] {p_id} - 리뷰 {len(df_reviews)}개 저장 완료')
      time.sleep(0.5)

    except Exception as e:
      print(f'{p_id} 처리 중 오류 발생: {e}')
      continue

  


