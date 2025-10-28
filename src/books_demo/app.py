from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from . import models, schemas
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="books_demo")


@app.get("/books", response_model=list[schemas.Book])
def get_books(db: Session = Depends(get_db)) -> list[schemas.Book]:
    return db.query(models.Book).all()
