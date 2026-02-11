from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# Load environment variables from .env file
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "sentilex")
DB_DRIVER = os.getenv("DB_DRIVER", "postgresql+psycopg2")

DATABASE_URL = f"{DB_DRIVER}://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=os.getenv("SQL_ECHO", "false").lower() in ("1", "true", "yes"))

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import text

def check_db_connection():
    try:
        # Create a temporary session to test connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print(f"Successfully connected to database: {DB_NAME}")
        return True
    except Exception as e:
        print(f"Error connecting to database '{DB_NAME}': {e}")
        return False
