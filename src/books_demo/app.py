from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import Session, select

from .database import engine, create_db_and_tables
from .models import Book


app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


@app.get("/books/")
def get_books():
    with Session(engine) as session:
        books = session.exec(select(Book)).all()
        return books
