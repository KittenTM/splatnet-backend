from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import OperationalError
from config import settings
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(16), unique=True, index=True, nullable=False)
    local_hash = Column(Text, nullable=False)
    spfn_pass_enc = Column(Text, nullable=False)

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(16), ForeignKey("users.username"), nullable=False)
    expires_at = Column(DateTime, nullable=True)
    remember_me = Column(Boolean, default=False)

engine = create_engine(settings.db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# TODO: look into why this is being called twice on startup
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("database tables ensured")
    except OperationalError as e:
        print(f"database connection error: {str(e)}")
        raise
    except Exception as e:
        print(f"database setup error: {str(e)}")
        raise

init_db()