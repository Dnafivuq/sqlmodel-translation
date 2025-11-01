from copy import deepcopy

from sqlalchemy import Column
from sqlalchemy.orm import column_property
from sqlmodel import Session, SQLModel, select, update

from books_demo import database as db
from books_demo import models as md
from books_demo.seed_data import seed_data


class TranslationOptions:
    fields: tuple[str] = ()
    languages: tuple[str] = ()


class BookTranslationOptions(TranslationOptions):
    fields = ("title",)
    languages = ("pl",)


class Translator:
    def register(self, model: type[SQLModel], translation_options: TranslationOptions) -> None:
        for field in translation_options.fields:
            for lang in translation_options.languages:
                field_name = f"{field}_{lang}"

                # TODO: check if field type is translatable
                orig_type = model.__table__.columns[field].type

                column = Column(field_name, orig_type, nullable=True)
                model.__table__.append_column(column)

                pydantic_field = deepcopy(model.model_fields[field])
                pydantic_field.alias = field_name
                model.model_fields[field_name] = pydantic_field

                orig_annotation = model.__annotations__[field]

                model.__annotations__[field_name] = orig_annotation

                setattr(model, field_name, column_property(column))

        model.model_rebuild(force=True)


if __name__ == "__main__":
    engine = db.create_db_engine()
    t = Translator()
    t.register(md.Book, BookTranslationOptions)

    db.create_db_and_tables(engine)
    seed_data(engine)

    with Session(engine) as session:
        statement = (
            update(md.Book)
            .where(md.Book.author == "J.R.R. Tolkien")
            .values(title_pl="translation")
        )
        session.exec(statement)
        stm = select(md.Book)
        books = session.exec(stm).all()

        print(books)
