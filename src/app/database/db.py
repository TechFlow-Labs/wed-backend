from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from environs import Env

env = Env()
env.read_env()


def _build_database_url() -> str:
    direct_url = env.str("DATABASE_URL", "")
    if direct_url:
        return direct_url

    db_user = env.str("DB_USER", "postgres")
    db_password = env.str("DB_PASSWORD", "postgres")
    db_host = env.str("DB_HOST", "postgres")
    db_port = env.str("DB_PORT", "5432")
    db_name = env.str("DB_DATABASE", "wedding_plan")
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


SQLALCHEMY_DATABASE_URL = _build_database_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(
    # autocommit=False,
    # autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
