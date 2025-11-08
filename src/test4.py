from copy import deepcopy

from sqlalchemy import Column
from sqlalchemy.orm import column_property
from sqlmodel import Session, SQLModel, select, update

from books_demo import database as db
from books_demo import models as md
from books_demo.seed_data import seed_data

from sqlalchemy import Column, Integer, String, select
from sqlalchemy.orm import declarative_base
from contextvars import ContextVar
from sqlmodel.main import SQLModelMetaclass
Base = declarative_base()
current_lang = ContextVar("lang", default="en")


def localize_class(cls, attr_names):
    class LocalizedMeta(SQLModelMetaclass):
        def __getattribute__(self, name):
            lang = current_lang.get()
            print("current lang: ", lang)

            if name in attr_names:
                localized = f"{name}_{lang}"
                if hasattr(cls, localized):
                    return getattr(cls, localized)
            return super().__getattribute__(name)


    cls.__class__ = LocalizedMeta
    return cls


localize_class(md.Book, ["title"])

print("CLFKHBA", md.Book.__class__)
if __name__ == "__main__":
    engine = db.create_db_engine()

    db.create_db_and_tables(engine)
    seed_data(engine)

    bok1 = md.Book(
        title="abc",
        author="dss",
    )
    print("HERE", bok1.__dict__)

    with Session(engine) as session:
        statement = (
            update(md.Book)
            .where(md.Book.author == "J.R.R. Tolkien")
            .values(title="translation")
        )
        session.exec(statement)
        stm = select(md.Book).where(md.Book.title == "translation")
        books = session.exec(stm).all()
