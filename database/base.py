# database/base.py
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# DATABASE_URL="postgresql://postgres:mysecretpassword@localhost:5432/mydatabase"
DATABASE_URL="postgresql://postgres:UptJgqycfITrDcWhBWaoXWQtbnviNoNk@caboose.proxy.rlwy.net:45718/railway"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)

Base = declarative_base()
