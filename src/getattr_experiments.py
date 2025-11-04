from sqlmodel import Field, Session, SQLModel, select

from books_demo import database as db

DEFAULT_LOCALE = "en"
CURRENT_LOCALE = "pl"
# Later swap this to ContextVars, maybe babel.

"""
Conclusions:
- overriding __setattr__ for translation is unsafe since it's used internally.
For example inserts might use fields based on locale and we only want this mechanism
when the user does Book.title on an instance

- overriding __getattr__ is probably safe and works exactly as we'd like
but needs to properly tested as there might be side effects

The solution is to probably make translated columns descriptors with custom
__get__ and __set__
"""


def translatable(cls: type[SQLModel]):
    original_init = cls.__init__
    original_getattribute = cls.__getattribute__
    original_setattr = cls.__setattr__

    # TranslationOptions containing translatable fields and languages
    # will be fetched here later. These are placeholders for now

    translated_fields = ("title",)
    languages = ("pl",)

    def __init__(self: SQLModel, **kwargs):
        original_init(self, **kwargs)

        for k, v in kwargs.items():
            if k in translated_fields and f"{k}_{CURRENT_LOCALE}" in kwargs:
                original_setattr(self, k, v)

    # Only update the original field if:
    # If it's given explicitly and the current language is also given
    
    # This might have bad side effects
    def __getattribute__(self: SQLModel, name: str):
        if name.startswith("_"):
            return original_getattribute(self, name)

        if (
            CURRENT_LOCALE in languages
            and CURRENT_LOCALE != DEFAULT_LOCALE
            and name in translated_fields
        ):
            return original_getattribute(self, f"{name}_{CURRENT_LOCALE}")

        return original_getattribute(self, name)

    # SQLModel/SQLite uses __setattr__ when inserting objects internally.
    # This means the translated columns get affected by locale when inserting
    # Which is bad!!!
    def __setattr__(self: SQLModel, name, value):
        if name.startswith("_"):
            return original_setattr(self, name, value)

        if (
            CURRENT_LOCALE in languages
            and CURRENT_LOCALE != DEFAULT_LOCALE
            and name in translated_fields
        ):
            return original_setattr(self, f"{name}_{CURRENT_LOCALE}", value)

        return original_setattr(self, name, value)

    cls.__init__ = __init__
    cls.__getattribute__ = __getattribute__
    cls.__setattr__ = __setattr__
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
            Book(title="The Hobbit", title_pl="Hobbit(PL)", author="J.R.R. Tolkien"),
            Book(title="1984", author="George Orwell"),
            Book(title="To Kill a Mockingbird", author="Harper Lee"),
        ]
        session.add_all(books)
        session.commit()

    with Session(engine) as session:
        print("\n\n")
        # stm = select(Book)
        # books = session.exec(stm).all()

        print("\n\n")
        stm2 = select(Book).where(Book.title == "1984")  # .where(Book.title_pl == "The Hobbit")
        books = session.exec(stm2).all()
        print(books)