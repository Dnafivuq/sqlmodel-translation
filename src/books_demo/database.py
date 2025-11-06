from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, create_engine


def create_db_engine(in_memory=True) -> Engine:
    sqlite_file_name = ":memory:" if in_memory else "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    connect_args = {"check_same_thread": False}
    return create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables(engine: Engine) -> None:
    SQLModel.metadata.create_all(engine)
