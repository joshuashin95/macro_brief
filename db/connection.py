"""
db/connection.py

Database connection using SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from utils.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_session():
    return Session()
