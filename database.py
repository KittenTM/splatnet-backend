from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, ForeignKey, Text, BigInteger, Float, func
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

class Equipment(Base):
    __tablename__ = 'equipment'
    PId = Column(BigInteger, primary_key=True)
    weapon = Column(Integer, primary_key=True)
    sumpaint = Column(Integer)

class EquipmentLast(Base):
    __tablename__ = 'equipment_last'
    PId = Column(BigInteger, primary_key=True)
    weapon = Column(Integer)
    Gear_Shoes = Column(Integer)
    Gear_Shoes_Skill0 = Column(Integer)
    Gear_Shoes_Skill1 = Column(Integer)
    Gear_Shoes_Skill2 = Column(Integer)
    Gear_Clothes = Column(Integer)
    Gear_Clothes_Skill0 = Column(Integer)
    Gear_Clothes_Skill1 = Column(Integer)
    Gear_Clothes_Skill2 = Column(Integer)
    Gear_Head = Column(Integer)
    Gear_Head_Skill0 = Column(Integer)
    Gear_Head_Skill1 = Column(Integer)
    Gear_Head_Skill2 = Column(Integer)
    Rank = Column(Integer)
    Udemae = Column(Integer)

class PlayerRank(Base):
    __tablename__ = 'player_ranks'

    PId = Column(BigInteger, primary_key=True, nullable=False)
    GameMode = Column(Integer, primary_key=True, nullable=False)
    MiiName = Column(String, nullable=True)
    Rank = Column(Integer, default=0)
    FesPower = Column(Float, default=0.0)
    WinSum = Column(Integer, default=0)
    LoseSum = Column(Integer, default=0)
    RankingScore = Column(Float, default=0.0)
    createdAt = Column(DateTime, server_default=func.now())
    updatedAt = Column(DateTime, onupdate=func.now())

class TwitterLink(Base):
    __tablename__ = "twitter_link"
    pid = Column(Integer, primary_key=True)
    twitter_handle = Column(String)
    twitter_token_enc = Column(String)
    twitter_refresh_token_enc = Column(String)
    miidata_enc = Column(String)

engine = create_engine(
    settings.db_url, 
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=30,
    pool_timeout=60,
    pool_recycle=1800
)
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