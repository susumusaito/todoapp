import os

from sqlmodel import SQLModel, Session, create_engine

# Vercel serverless: /tmp is the only writable directory
if os.environ.get("VERCEL"):
    DATABASE_URL = "sqlite:////tmp/todo.db"
else:
    DATABASE_URL = "sqlite:///todo.db"

engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
