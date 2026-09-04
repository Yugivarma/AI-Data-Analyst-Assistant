import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('PG_USER')}:"
    f"{os.getenv('PG_PASSWORD')}@"
    f"{os.getenv('PG_HOST')}:"
    f"{os.getenv('PG_PORT')}/"
    f"{os.getenv('PG_DB')}"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()