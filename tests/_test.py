from sqlmodel import select, update


def test_books_inserted(book_cls, book_seed_data) -> None:
    session = book_seed_data

    books = session.exec(select(book_cls)).all()

    assert len(books) == 3
    assert books[0].title == "The Hobbit"


def test_books_translated_inserted(translator_en_pl_instance, book_seed_data) -> None:
    session = book_seed_data
    translator, book_cls = translator_en_pl_instance

    translator.set_active_language("en")

    stm = select(book_cls).where(book_cls.author == "J.R.R. Tolkien")
    books = session.exec(stm).all()

    assert books[0].title == "The Hobbit"

    translator.set_active_language("pl")

    statement = update(book_cls).where(book_cls.author == "J.R.R. Tolkien").values(title="translation")
    session.exec(statement)

    stm = select(book_cls).where(book_cls.author == "J.R.R. Tolkien")
    books = session.exec(stm).all()

    assert books[0].title == "translation"


def test_books_translated_inserted2(translator_es_gb_instance, book_seed_data) -> None:
    session = book_seed_data
    translator, book_cls = translator_es_gb_instance

    translator.set_active_language("es")

    stm = select(book_cls).where(book_cls.author == "J.R.R. Tolkien")
    books = session.exec(stm).all()

    assert books[0].title == "The Hobbit"

    translator.set_active_language("gb")

    statement = update(book_cls).where(book_cls.author == "J.R.R. Tolkien").values(title="translation")
    session.exec(statement)

    stm = select(book_cls).where(book_cls.author == "J.R.R. Tolkien")
    books = session.exec(stm).all()

    assert books[0].title == "translation"
