from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session, select

from .database import create_db_and_tables, create_db_engine, seed_data
from .models import Book

engine = create_db_engine()


@asynccontextmanager
async def lifespan():
    create_db_and_tables(engine)
    seed_data(engine)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/books/")
def get_books() -> Book:
    with Session(engine) as session:
        return session.exec(select(Book)).all()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
