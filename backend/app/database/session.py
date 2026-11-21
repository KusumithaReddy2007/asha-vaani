from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from app.core.config import settings

# For SQLite, check_same_thread=False and NullPool prevent locked file errors on Windows
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 20}
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        poolclass=NullPool,
        echo=False
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
