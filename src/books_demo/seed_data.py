from sqlmodel import Session, select

from .models import Book

# In separate file to not confict with test objects named Book when importing database.py


def seed_data(engine) -> None:
    with Session(engine) as session:
        if not session.exec(select(Book)).first():
            books = [
                Book(title="The Hobbit", author="J.R.R. Tolkien"),
                Book(title="1984", author="George Orwell"),
                Book(title="To Kill a Mockingbird", author="Harper Lee"),
            ]
            session.add_all(books)
            session.commit()
