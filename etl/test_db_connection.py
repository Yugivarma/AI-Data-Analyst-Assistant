import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

host = os.getenv("PG_HOST", "localhost")
port = os.getenv("PG_PORT", "5432")
db = os.getenv("PG_DB", "ai_data_analyst")
user = os.getenv("PG_USER", "postgres")
password = os.getenv("PG_PASSWORD")

engine = create_engine(
    f"postgresql+psycopg2://"
    f"{user}:{password}@{host}:{port}/{db}"
)

with engine.connect() as connection:
    result = connection.execute(
        text("SELECT current_database(), current_user;")
    )

    print("Database connection successful!")
    print(result.fetchone())