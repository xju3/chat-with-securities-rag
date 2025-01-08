
from sqlalchemy import create_engine
from dotenv import load_dotenv, find_dotenv
import os


def get_engine():
    load_dotenv(find_dotenv())
    print(os.getenv("PG_HOST"))
    return create_engine(f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASS')}@{os.getenv('PG_HOST')}/{os.getenv('PG_DB')}")