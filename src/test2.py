from copy import deepcopy

from pydantic import Field
from sqlalchemy import Column
from sqlalchemy.orm import column_property
from sqlmodel import Session, SQLModel, select, update

from books_demo import database as db

# Decorator version of test.py (Not working though)


class TranslationOptions:
    fields: tuple[str] = ()
    languages: tuple[str] = ()


class BookTranslationOptions(TranslationOptions):
    fields = ("title",)
    languages = ("pl",)


class Translator:
    def register(self, translation_options: type[TranslationOptions]) -> None:
        def wrapper(cls: type[SQLModel]) -> type[SQLModel]:
            for field in translation_options.fields:
                for lang in translation_options.languages:
                    field_name = f"{field}_{lang}"
                    if field_name in cls.__annotations__:
                        continue
                    # TODO: check if field type is translatable
                    orig_type = cls.__table__.columns[field].type

                    column = Column(field_name, orig_type, nullable=True)
                    cls.__table__.append_column(column)

                    pydantic_field = deepcopy(cls.cls_fields[field])
                    pydantic_field.alias = field_name
                    cls.cls_fields[field_name] = pydantic_field

                    orig_annotation = cls.__annotations__[field]

                    cls.__annotations__[field_name] = orig_annotation

                    setattr(cls, field_name, column_property(column))

            cls.model_rebuild(force=True)
            return cls

        return wrapper


t = Translator()


@t.register(BookTranslationOptions)
class Book2(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author: str


if __name__ == "__main__":
    engine = db.create_db_engine()

    db.create_db_and_tables()

    with Session(engine) as session:
        if not session.exec(select(Book2)).first():
            books = [
                Book2(title="The Hobbit", author="J.R.R. Tolkien"),
                Book2(title="1984", author="George Orwell"),
                Book2(title="To Kill a Mockingbird", author="Harper Lee"),
            ]
            session.add_all(books)
            session.commit()
    with Session(engine) as session:
        statement = (
            update(Book2).where(Book2.author == "J.R.R. Tolkien").values(title_pl="translation")
        )
        session.exec(statement)
        stm = select(Book2)
        books = session.exec(stm).all()

        print(books)
