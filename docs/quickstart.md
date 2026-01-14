# Quickstart

To demonstrate how to use this library we will write a simple FastAPI application.
The full example is available at examples/quickstart.py.

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


@app.get("/all")
def get_books() -> list[Book]:
    with Session(engine) as session:
        return session.exec(select(Book)).all()


@app.get("/titles")
def get_titles() -> list[Book]:
    with Session(engine) as session:
        return session.exec(select(Book.title)).all()


@app.post("/create")
def create_book(book: Book) -> Book:
    with Session(engine) as session:
        session.add(book)
        session.commit()
        session.refresh(book)
        return book

```
We can now run the server with `fastapi dev quickstart.py`.
The server by default runs on `http://127.0.0.1:8000`, with docs at `http://127.0.0.1:8000/docs`.

Now we will look at how translations are handled in endpoints.

`/all` returns a list of books with translated titles.

    [
      {
        "author": "J.R.R. Tolkien",
        "title": "english_title_1",
        "id": 1
      },
      {
        "author": "Harper Lee",
        "title": "english_title_2",
        "id": 2
      }
    ]
`/titles` returns translated titles.

    [
      "english_title_1",
      "english_title_2"
    ]

We can also take a look at the schema for `/create` using the FastAPI docs.

    {
      "id": 0,
      "title": "string",
      "author": "string",
      "title_en": "string",
      "title_pl": "string"
    }
When creating a `Book` you we can specify all translation fields manually,
or use the `title` field and let it redirect based on the active language.


[`Translator`][modeltranslation.Translator], and [`TranslationOptions`][modeltranslation.TranslationOptions] support other configuration options regarding required languages, and fallback behaviour.

