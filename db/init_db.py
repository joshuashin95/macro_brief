"""
db/init_db.py

Creates all tables in PostgreSQL. Run once to initialize the database.

Usage:
    python -m db.init_db
"""

from db.connection import engine
from db.schema import Base


def init():
    Base.metadata.create_all(engine)
    print("Tables created successfully.")
    for table in Base.metadata.tables:
        print(f"  - {table}")


if __name__ == "__main__":
    init()
