from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from core.settings import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True,
                       connect_args={'check_same_thread': False} if DATABASE_URL.startswith('sqlite:') else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    with SessionLocal() as db:
        yield db
