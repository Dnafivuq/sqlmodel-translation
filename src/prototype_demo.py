from sqlmodel import Field, Session, SQLModel, select, update

from books_demo import database as db
from modeltranslation.translator import TranslationOptions, Translator

translator = Translator("en", ("en", "pl"))
engine = db.create_db_engine()


class Book(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    author: str


@translator.register(Book)
class BookTranslationOptions(TranslationOptions):
    fields = ("title",)
    required_languages = ("pl",)

db.create_db_and_tables(engine)


with Session(engine) as session:
    print("\n\n Test start")
    translator.set_active_language("pl")
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
    translator.set_active_language("pl")
    statement = update(Book).where(Book.author == "J.R.R. Tolkien").values(title="translation")
    session.exec(statement)

    print("\n")
    stm = select(Book).where(Book.title == "translation")
    books = session.exec(stm).all()
    print("\n")
