import pytest
from sqlalchemy.engine import Engine
from sqlmodel import Field, Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from src.modeltranslation.translator import TranslationOptions, Translator


@pytest.fixture(autouse=True)
def clear_metadata() -> None:
    SQLModel.metadata.clear()


@pytest.fixture
def engine_instance():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    yield engine
    engine.dispose()


@pytest.fixture
def book_instance():
    class Book(SQLModel, table=True):
        id: int = Field(default=None, primary_key=True)
        title: str | None
        author: str

    return Book


@pytest.fixture
def create_db_and_tables(engine_instance: Engine):
    SQLModel.metadata.create_all(engine_instance)
    yield
    SQLModel.metadata.drop_all(engine_instance)


@pytest.fixture
def translator_pl_en_instance(book_instance) -> None:
    translator = Translator("en")

    @translator.register(book_instance)
    class BookTranslationOptions(TranslationOptions):
        fields = ("title",)
        languages = ("pl", "en")

    return translator, book_instance


@pytest.fixture
def translator_es_gb_instance(book_instance) -> None:
    translator = Translator("es")
    translator.set_locale("es")

    @translator.register(book_instance)
    class BookTranslationOptions(TranslationOptions):
        fields = ("title",)
        languages = ("es", "gb")

    return translator, book_instance


@pytest.fixture
def session_instance(engine_instance: Engine, create_db_and_tables):
    with Session(engine_instance) as session:
        yield session


@pytest.fixture
def book_seed_data(session_instance, book_instance):
    session = session_instance
    if not session.exec(select(book_instance)).first():
        books = [
            book_instance(title="The Hobbit", author="J.R.R. Tolkien"),
            book_instance(title="1984", author="George Orwell"),
            book_instance(title="To Kill a Mockingbird", author="Harper Lee"),
        ]
        session.add_all(books)
        session.commit()
    yield session_instance
