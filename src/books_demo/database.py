from sqlmodel import SQLModel, Session, create_engine, select
from .models import Book


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def seed_data():
    with Session(engine) as session:
        if not session.exec(select(Book)).first():
            books = [
                Book(title="The Hobbit", author="J.R.R. Tolkien"),
                Book(title="1984", author="George Orwell"),
                Book(title="To Kill a Mockingbird", author="Harper Lee"),
            ]
            session.add_all(books)
            session.commit()
