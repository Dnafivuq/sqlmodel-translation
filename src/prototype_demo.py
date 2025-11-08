from sqlmodel import Field, Session, SQLModel, select, update

from books_demo import database as db
from modeltranslation.translator import TranslationOptions, Translator, TranslatorMetaclass, register

Translator.set_locale("en")
engine = db.create_db_engine()


class BookTranslationOptions(TranslationOptions):
    fields = ("title",)
    languages = ("pl", "en")


# @register(translation_options=BookTranslationOptions)
class Book(
    SQLModel,
    table=True,
    metaclass=TranslatorMetaclass,
    translation_options=BookTranslationOptions,
):
    id: int = Field(primary_key=True)
    title: str | None
    author: str


register(Book, BookTranslationOptions)


db.create_db_and_tables(engine)


with Session(engine) as session:
    if not session.exec(select(Book)).first():
        books = [
            Book(title="The Hobbit", author="J.R.R. Tolkien"),
            Book(title="1984", author="George Orwell"),
            Book(title="To Kill a Mockingbird", author="Harper Lee"),
        ]
        session.add_all(books)
        session.commit()

with Session(engine) as session:
    print("\n\n Test start")
    statement = update(Book).where(Book.author == "J.R.R. Tolkien").values(title="translation")
    session.exec(statement)

    print("\n")
    Translator.set_locale("pl")
    stm = select(Book).where(Book.title == "translation")
    books = session.exec(stm).all()
    print("\n")
    print(books)
