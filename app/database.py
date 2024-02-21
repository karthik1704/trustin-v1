from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .settings import Debug
import os
load_dotenv()

username = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')



def get_database_url():
    print(Debug)
    if Debug:
        return f"postgresql+psycopg://postgres:postgres@localhost/trustin_fa"
    else:

        return f"postgresql+psycopg://{username}:{password}@{host}/{db_name}"



SQLALCHEMY_DATABASE_URL = get_database_url()


engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
