from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer , String, Float, BigInteger, Text , DateTime ,ForeignKey ,Double
from sqlalchemy.orm import relationship

Base = declarative_base()

class Restaurant(Base):
  __tablename__ = 'restaurants'

  place_id = Column(String(20), primary_key=True)
  name = Column(String(200))
  address = Column(String(300))
  new_address = Column(String(300))
  lon = Column(Double)
  lat = Column(Double)
  tel = Column(String(50))
  category_depth1 = Column(String(50))
  category_depth2 = Column(String(50))
  category_depth3 = Column(String(50))
  category_depth4 = Column(String(50))
  category_depth5 = Column(String(50))
  rating_average = Column(Float)
  rating_count = Column(Integer)
  img = Column(String(500))

  #외래키의 위치를 판단하여 1:N 이나 1:1의 관계를 구별하여 정의함 양방향 설계함 (외래키가 있는쪽이 N이다.)
  reviews = relationship("Review", back_populates="restaurant", cascade="all, delete")


class Review(Base):
  __tablename__ = 'reviews'

  review_id = Column(BigInteger, primary_key=True)
  place_id = Column(String(20), ForeignKey('restaurants.place_id', ondelete='CASCADE'))
  star_rating = Column(Integer)
  contents = Column(Text)
  registered_at = Column(DateTime)
  updated_at = Column(DateTime)
  strength = Column(String(255))

  # 관계 정의 (테이블에 외래키가 있으므로 외래키가 참조하는 테이블이 1:N에서 1이다.)
  restaurant = relationship("Restaurant", back_populates="reviews")