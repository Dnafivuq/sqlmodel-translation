from typing import Annotated

import pytest
from pydantic import StringConstraints, ValidationError
from sqlmodel import Field, Session, SQLModel, select, update

from src.modeltranslation import TranslationOptions, Translator


def test_translation_registers_without_errors() -> None:
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


def test_translated_model_fields_exist() -> None:
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

    for lang in ("en", "pl"):
        field_name = f"title_{lang}"
        assert hasattr(Book, field_name)

    book = Book()
    for lang in ("en", "pl"):
        field_name = f"title_{lang}"
        assert hasattr(book, field_name)


def test_field_redirected_to_translation(
    translator_en_pl_instance: tuple[Translator, type[SQLModel]],
) -> None:
    translator, book_cls = translator_en_pl_instance

    translator.set_active_language("en")
    book = book_cls(author="123", title="english")

    assert book.title_en == "english"
    assert book.title == "english"
    assert book.title_pl is None

    translator.set_active_language("pl")
    book.title = "polish"
    book.title_en = "english2"

    assert book.title_en == "english2"
    assert book.title == "polish"
    assert book.title_pl == "polish"


def test_pydantic_rebuilt_correctly(book_cls: type[SQLModel]) -> None:
    translator = Translator(
        default_language="en",
        languages=("en", "pl"),
    )

    @translator.register(book_cls)
    class BookTranslationOptions(TranslationOptions):
        fields = ("title",)
        required_languages = ("pl",)

    fields = book_cls.model_fields
    assert "title_en" in fields
    assert "title_pl" in fields


def test_pydantic_rebuilt_correctly_2() -> None:
    class Book(SQLModel, table=True):
        id: int | None = Field(default=None, primary_key=True)
        title: Annotated[str, StringConstraints(max_length=3)]

    translator = Translator(
        default_language="en",
        languages=("en", "pl"),
    )
    translator.set_active_language("en")

    Book.model_validate(Book(title="123"))

    with pytest.raises(ValidationError):
        Book.model_validate(Book(title="1234"))

    @translator.register(Book)
    class BookTranslationOptions(TranslationOptions):
        fields = ("title",)
        required_languages = ("pl",)

    Book.model_validate(Book(title_pl="123"))
    Book.model_validate(Book(title_en="123"))
    Book.model_validate(Book(title="123"))

    with pytest.raises(ValidationError):
        Book.model_validate(Book(title="1234"))

    with pytest.raises(ValidationError):
        Book.model_validate(Book(title_en="1234"))

    with pytest.raises(ValidationError):
        Book.model_validate(Book(title_pl="1234"))


def test_title_redirected_in_queries(
    translator_en_pl_instance: tuple[Translator, type[SQLModel]], session: Session
) -> None:
    translator, book_cls = translator_en_pl_instance

    translator.set_active_language("pl")

    book_created = book_cls(title_en="english_title", author="123")
    session.add(book_created)

    translator.set_active_language("en")

    stm = select(book_cls).where(book_cls.title == "english_title")
    book = session.exec(stm).first()

    assert book.title == "english_title"
    assert book.title_pl is None


def test_title_redirected_in_queries_update(
    translator_en_pl_instance: tuple[Translator, type[SQLModel]], book_seed_data: Session
) -> None:
    translator, book_cls = translator_en_pl_instance
    session = book_seed_data

    translator.set_active_language("pl")

    stm = update(book_cls).values(title="polish")
    session.exec(stm)

    stm = select(book_cls)
    books = session.exec(stm).all()

    for book in books:
        assert book.title_pl == "polish"
        assert book.title == "polish"


@pytest.mark.todo("Translator should not let you set a language not specified in languages")
def test_translator_set_invalid_language() -> None:
    translator = Translator(
        default_language="en",
        languages=("en", "pl"),
    )
    translator.set_active_language("fr")


# It might be good to check this for any other field
@pytest.mark.todo(
    "Throw error or provide a message when the TranslationOptions "
    "languages sets a language not included in the translator"
)
def test_translation_register_undefined_lang(book_cls: type[SQLModel]) -> None:
    translator = Translator(
        default_language="en",
        languages=("en", "pl"),
    )

    @translator.register(book_cls)
    class BookTranslationOptions(TranslationOptions):
        fields = ("title",)
        required_languages = ("fr",)


def test_translation_required_lang_annotations() -> None:
    class Book(SQLModel, table=True):
        id: int | None = Field(default=None, primary_key=True)
        title: str

    translator = Translator(
        default_language="en",
        languages=("en", "pl"),
    )

    @translator.register(Book)
    class BookTranslationOptions(TranslationOptions):
        fields = ("title",)
        required_languages = ("en",)

    annotations = Book.__annotations__
    assert annotations["title"] == (str | None)
    assert annotations["title_pl"] == (str | None)
    assert annotations["title_en"] is str


def test_translation_required_lang_annotations_optional() -> None:
    class Book(SQLModel, table=True):
        id: int | None = Field(default=None, primary_key=True)
        title: str | None

    translator = Translator(
        default_language="en",
        languages=("en", "pl"),
    )

    @translator.register(Book)
    class BookTranslationOptions(TranslationOptions):
        fields = ("title",)
        required_languages = ("en",)

    annotations = Book.__annotations__
    assert annotations["title"] == (str | None)
    assert annotations["title_pl"] == (str | None)
    assert annotations["title_en"] == (str | None)


def test_translation_() -> None:
    class Book(SQLModel, table=True):
        id: int | None = Field(default=None, primary_key=True)
        title: str | None

    translator = Translator(
        default_language="en",
        languages=("en", "pl"),
    )

    @translator.register(Book)
    class BookTranslationOptions(TranslationOptions):
        fields = ("title",)
        required_languages = ("en",)

    annotations = Book.__annotations__
    assert annotations["title"] == (str | None)
    assert annotations["title_pl"] == (str | None)
    assert annotations["title_en"] == (str | None)
