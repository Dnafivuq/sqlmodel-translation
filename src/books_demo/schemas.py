from pydantic import BaseModel


class BookBase(BaseModel):
    title: str
    author: str


class Book(BookBase):
    id: int

    class Config:
        orm_mode = True
