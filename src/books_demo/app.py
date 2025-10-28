from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import Session, select

from .database import engine, create_db_and_tables, seed_data
from .models import Book


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_data()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/books/")
def get_books():
    with Session(engine) as session:
        books = session.exec(select(Book)).all()
        return books
