from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# SQLite setup for development
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def create_db_and_tables():
    import app.models.memory # Ensure model is registered
    # Create all tables stored in this metadata.
    Base.metadata.create_all(bind=engine)

def get_session():
    with SessionLocal() as session:
        yield session
