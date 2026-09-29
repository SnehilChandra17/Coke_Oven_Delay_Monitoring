import os

from urllib.parse import quote_plus

from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# ---------------------------------------------------------
# LOAD ENVIRONMENT VARIABLES
# ---------------------------------------------------------

load_dotenv()


# ---------------------------------------------------------
# DATABASE CONFIGURATION
# ---------------------------------------------------------

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv(
    "DB_NAME",
    "coke_oven_monitoring"
)


# ---------------------------------------------------------
# VALIDATE DATABASE CONFIGURATION
# ---------------------------------------------------------

if not DB_USER:
    raise ValueError(
        "DB_USER is missing from .env"
    )

if not DB_PASSWORD:
    raise ValueError(
        "DB_PASSWORD is missing from .env"
    )


# ---------------------------------------------------------
# ENCODE PASSWORD
# ---------------------------------------------------------

encoded_password = quote_plus(
    DB_PASSWORD
)


# ---------------------------------------------------------
# DATABASE URL
# ---------------------------------------------------------

DATABASE_URL = (
    f"mysql+pymysql://"
    f"{DB_USER}:"
    f"{encoded_password}"
    f"@{DB_HOST}/"
    f"{DB_NAME}"
)


# ---------------------------------------------------------
# SQLALCHEMY
# ---------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    echo=False
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


# ---------------------------------------------------------
# DATABASE SESSION
# ---------------------------------------------------------

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()