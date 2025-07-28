import openai
import pandas as pd
from sqlalchemy.orm import sessionmaker
from db_connection import get_engine
from crawler.db_table import Review, ReviewAnalysis
from datetime import datetime,timezone
import time
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
from dotenv import load_dotenv
import os

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

# DB 연결 
engine = get_engine()
Session = sessionmaker(bind=engine)
session = Session()







