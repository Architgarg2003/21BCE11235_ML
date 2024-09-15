from sqlalchemy import create_engine, Column, Integer, String, Text, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(String(50), primary_key=True)
    request_count = Column(Integer, default=0)

class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, primary_key=True)
    filename = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    embedding = Column(PickleType)

# Set up the SQLite engine and session
engine = create_engine('sqlite:///app.db')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()