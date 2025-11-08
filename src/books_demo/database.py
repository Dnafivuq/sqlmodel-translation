import tempfile

from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine


def create_db_engine(in_memory=False) -> Engine:
    if in_memory:
        sqlite_file_name = ":memory:"
    else:
        sqlite_file_name = tempfile.NamedTemporaryFile(delete=False, suffix=".db").name

    sqlite_url = f"sqlite:///{sqlite_file_name}"

    connect_args = {"check_same_thread": False}
    return create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables(engine: Engine) -> None:
    SQLModel.metadata.create_all(engine)
