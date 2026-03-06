import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# .env 파일 로드 (환경변수)
load_dotenv()

# PostgreSQL DB URL (예: postgresql://user:password@localhost/mugang_db)
# 로컬 테스트를 위해 임시 sqlite 사용 가능, 가이드라인에 따라 PostgreSQL 주소 입력 필요
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

_is_sqlite = "sqlite" in SQLALCHEMY_DATABASE_URL

engine_args = {
    "connect_args": {"check_same_thread": False} if _is_sqlite else {}
}

if not _is_sqlite:
    engine_args.update({
        "pool_size": 20,
        "max_overflow": 30,
        "pool_pre_ping": False,
        "pool_recycle": 3600,
        "pool_timeout": 10
    })

engine = create_engine(SQLALCHEMY_DATABASE_URL, **engine_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# DB 세션 의존성 주입용 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
