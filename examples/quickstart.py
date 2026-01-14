from fastapi import FastAPI
from sqlmodel import Field, Session, SQLModel, StaticPool, create_engine, select

from modeltranslation import TranslationOptions, Translator, apply_translation

engine = create_engine(
    "sqlite://",
    echo=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: str


translator = Translator(
    default_language="en",
    languages=("en", "pl"),
)


@translator.register(Book)
class BookTranslationOptions(TranslationOptions):
    fields = ("title",)


create_db_and_tables()

books = [
    Book(title_en="english_title_1", title_pl="polish_title_1", author="J.R.R. Tolkien"),
    Book(title_en="english_title_2", title_pl="polish_title_2", author="Harper Lee"),
]

with Session(engine) as session:
    session.add_all(books)
    session.commit()


app = FastAPI()

apply_translation(app, translator)


@app.get("/all")
def get_books() -> list[Book]:
    with Session(engine) as session:
        return session.exec(select(Book)).all()


@app.get("/titles")
def get_titles() -> list[str]:
    with Session(engine) as session:
        return session.exec(select(Book.title)).all()


@app.post("/create")
def create_book(book: Book) -> Book:
    with Session(engine) as session:
        session.add(book)
        session.commit()
        session.refresh(book)
        return book
