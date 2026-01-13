# Quickstart

To demonstrate how to use this library we will write a simple FastAPI application.

First we will create a sqlite database.

```python
from sqlmodel import Field, Session, SQLModel, StaticPool, create_engine

engine = create_engine(
    "sqlite://",
    echo=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

To begin create a Book class.
```python
class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: str
```

To make Book translatable you need to create a [`Translator`][modeltranslation.Translator], [`TranslationOptions`][modeltranslation.TranslationOptions] and register the `TranslationOptions` for your class.

```python
from modeltranslation import TranslationOptions, Translator

translator = Translator(
    default_language='en',
    languages=('en', 'pl'),
)

@translator.register(Book)
class BookTranslationOptions(TranslationOptions):
    fields = ("title",)

```

As a result `Book` gained 2 new fields - Book.title_en, Book.title_pl.
We can now do:

```python
book = Book(title = '1984', author='George Orwell')
assert book.title == '1984'
assert book.title_en == '1984'
assert book.title_pl is None

```
Notice how `book.title == book.title_en`.

The translated `title` is redirected to the field for the current active language which is english.
That's because we created the translator with `default_language='en'`.


The new fields also work in all SQLModel queries and get transformed based on the active language.
```python
from sqlmodel import select

# These are equivalent
select(Book).where(Book.title == "english translation")
select(Book).where(Book.title_en == "english translation")

```

Before moving on we will add more books to the database.
```python
create_db_and_tables()

books = [
    Book(title_en="english_title_1", title_pl="polish_title_1", author="J.R.R. Tolkien"),
    Book(title_en="english_title_2", title_pl="polish_title_2", author="Harper Lee"),
]
with Session(engine) as session:
    session.add_all(books)
    session.commit()

```

To integrate the project with FastAPI we use the [`apply_translation`][modeltranslation.apply_translation].
This makes FastAPI set the active language for each request based on the `Accept-Language` HTTP header.

```python
from modeltranslation import apply_translation
from fastapi import FastAPI


app = FastAPI()

apply_translation(app, translator)


@app.get("/books")
def get_books() -> list[Book]:
    with Session(engine) as session:
        return session.exec(select(Book)).all()


@app.get("/titles")
def get_titles() -> list[Book]:
    with Session(engine) as session:
        return session.exec(select(Book.title)).all()
```

If we run the server and use the `/titles` endpoint, we will either see all titles in enlish or polish.


[`Translator`][modeltranslation.Translator], and [`TranslationOptions`][modeltranslation.TranslationOptions] support other configuration options regarding required languages, and fallback behaviour.

