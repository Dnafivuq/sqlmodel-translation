from collections.abc import Generator
from typing import Any

import pytest
from sqlalchemy.engine import Engine
from sqlalchemy.orm import clear_mappers
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from src.modeltranslation.translator import TranslationOptions, Translator


@pytest.fixture(autouse=True)
def clear_metadata() -> None:
    clear_mappers()
    SQLModel.metadata.clear()


@pytest.fixture
def engine() -> Generator[Engine, Any, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    yield engine
    engine.dispose()


@pytest.fixture
def book_cls() -> type[SQLModel]:
    class Book(SQLModel, table=True):
        id: int | None = Field(default=None, primary_key=True)
        title: str
        author: str

    return Book


@pytest.fixture
def create_db_and_tables(engine: Engine) -> Generator[None, Any, None]:
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def translator_en_pl_instance(book_cls: type[SQLModel]) -> tuple[Translator, type[SQLModel]]:
    translator = Translator(
        default_language="en",
        languages=("en", "pl"),
    )

    @translator.register(book_cls)
    class BookTranslationOptions(TranslationOptions):
        fields = ("title",)
        required_languages = ("en",)

    return translator, book_cls


@pytest.fixture
def translator_es_gb_instance(book_cls: type[SQLModel]) -> tuple[Translator, type[SQLModel]]:
    translator = Translator(
        default_language="es",
        languages=("es", "gb"),
    )

    translator.set_active_language("es")

    @translator.register(book_cls)
    class BookTranslationOptions(TranslationOptions):
        fields = ("title",)

    return translator, book_cls


@pytest.fixture
def session(
    engine: Engine,
    create_db_and_tables: None,
) -> Generator[Session, Any, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture
def book_seed_data(session: Session, book_cls: type[SQLModel]):
    if not session.exec(select(book_cls)).first():
        books = [
            book_cls(title="The Hobbit", author="J.R.R. Tolkien"),
            book_cls(title="1984", author="George Orwell"),
            book_cls(title="To Kill a Mockingbird", author="Harper Lee"),
        ]
        session.add_all(books)
        session.commit()

    return session
