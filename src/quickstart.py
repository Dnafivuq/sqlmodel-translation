from sqlmodel import Field, Session, SQLModel, StaticPool, create_engine

engine = create_engine(
    "sqlite://",
    echo=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: str


from modeltranslation import TranslationOptions, Translator

translator = Translator(
    default_language="en",
    languages=("en", "pl"),
)


@translator.register(Book)
class BookTranslationOptions(TranslationOptions):
    fields = ("title",)


book = Book(title="1984", author="George Orwell")
assert book.title == "1984"
assert book.title_en == "1984"
assert book.title_pl is None


from sqlmodel import select

select(Book).where(Book.title == "english translation")
select(Book).where(Book.title_en == "english translation")


create_db_and_tables()

books = [
    Book(title_en="english_title_1", title_pl="polish_title_1", author="J.R.R. Tolkien"),
    Book(title_en="english_title_2", title_pl="polish_title_2", author="Harper Lee"),
]
with Session(engine) as session:
    session.add_all(books)
    session.commit()


from fastapi import FastAPI

from modeltranslation import apply_translation

app = FastAPI()

apply_translation(app, translator)


@app.get("/books")
def get_books() -> list[Book]:
    with Session(engine) as session:
        return session.exec(select(Book)).all()


@app.get("/titles")
def get_books() -> list[str]:
    with Session(engine) as session:
        return session.exec(select(Book.title)).all()
