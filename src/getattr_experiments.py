from sqlmodel import Field, Session, SQLModel, select

from books_demo import database as db

DEFAULT_LOCALE = "en"
CURRENT_LOCALE = "pl"
# Later swap this to ContextVars, maybe babel.


def translatable(cls: type[SQLModel]):
    original_getattribute = cls.__getattribute__
    original_setattr = cls.__setattr__

    translated_fields = ("title",)
    languages = ("pl",)

    def new_getattribute(self: SQLModel, name: str) -> any:
        if name.startswith("_"):
            return original_getattribute(self, name)

        if (
            CURRENT_LOCALE in languages
            and CURRENT_LOCALE != DEFAULT_LOCALE
            and name in translated_fields
        ):
            return original_getattribute(self, f"{name}_{CURRENT_LOCALE}")

        return original_getattribute(self, name)

    def new_setattr(self: SQLModel, name: str, value: any) -> None:
        if name.startswith("_"):
            return original_setattr(self, name, value)

        if (
            CURRENT_LOCALE in languages
            and CURRENT_LOCALE != DEFAULT_LOCALE
            and name in translated_fields
        ):
            return original_setattr(self, f"{name}_{CURRENT_LOCALE}", value)

        return original_setattr(self, name, value)

    cls.__getattribute__ = new_getattribute
    cls.__setattr__ = new_setattr
    return cls


@translatable
class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str | None
    title_pl: str | None
    author: str


if __name__ == "__main__":
    engine = db.create_db_engine()

    db.create_db_and_tables(engine)

    with Session(engine) as session:
        books = [
            Book(title="The Hobbit", author="J.R.R. Tolkien"),
            Book(title="1984", author="George Orwell"),
            Book(title="To Kill a Mockingbird", author="Harper Lee"),
        ]
        session.add_all(books)
        session.commit()

    with Session(engine) as session:
        print("\n\n")
        stm2 = select(Book)
        books = session.exec(stm2).all()
        print(books)
