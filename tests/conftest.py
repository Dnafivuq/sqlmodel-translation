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
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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
def translator_pl_en_instance(book_instance):
    translator = Translator(
        default_language="en",
        languages=("en", "pl"),
    )

    @translator.register(book_instance)
    class BookTranslationOptions(TranslationOptions):
        fields = ("title",)
        required_languages = ("en",)

    return translator, book_instance


@pytest.fixture
def translator_es_gb_instance(book_instance):
    translator = Translator(
        default_language="es",
        languages=("es", "gb"),
    )

    translator.set_active_language("es")

    @translator.register(book_instance)
    class BookTranslationOptions(TranslationOptions):
        fields = ("title",)

    return translator, book_instance


@pytest.fixture
def session_instance(
    engine_instance: Engine,
    create_db_and_tables,
):
    with Session(engine_instance) as session:
        yield session


@pytest.fixture
def book_seed_data(session_instance: Session, book_instance):
    if not session_instance.exec(select(book_instance)).first():
        books = [
            book_instance(title="The Hobbit", author="J.R.R. Tolkien"),
            book_instance(title="1984", author="George Orwell"),
            book_instance(title="To Kill a Mockingbird", author="Harper Lee"),
        ]
        session_instance.add_all(books)
        session_instance.commit()

    return session_instance
