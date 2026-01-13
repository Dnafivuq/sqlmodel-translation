from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session, select

from modeltranslation.locale_manager import apply_translation
from modeltranslation.translator import TranslationOptions, Translator

from .database import create_db_and_tables, create_db_engine
from .models import Book
from .seed_data import seed_data

translator = Translator(
    default_language="en",
    languages=("en", "pl"),
)

engine = create_db_engine(in_memory=False)


@translator.register(Book)
class BookTranslationOptions(TranslationOptions):
    fields = ("title",)
    required_languages = ("en",)


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db_and_tables(engine)
    seed_data(engine)
    yield


app = FastAPI(lifespan=lifespan)

apply_translation(app, translator)


@app.get("/books/")
def get_books() -> list[Book]:
    with Session(engine) as session:
        return session.exec(select(Book)).all()


@app.get("/books/titles", response_model=list[str])
def get_books_titles() -> list[Book]:
    with Session(engine) as session:
        books = session.exec(select(Book)).all()
        return [book.title for book in books]

@app.post("/books/", response_model=Book)
def create_book(book: Book) -> Book:
    with Session(engine) as session:
        session.add(book)
        session.commit()
        session.refresh(book)
        return book
