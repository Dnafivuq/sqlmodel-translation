from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session, select

from .database import create_db_and_tables, create_db_engine
from .models import Book
from .seed_data import seed_data

engine = create_db_engine(in_memory=False)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables(engine)
    seed_data(engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/books/")
def get_books() -> list[Book]:
    with Session(engine) as session:
        return session.exec(select(Book)).all()
