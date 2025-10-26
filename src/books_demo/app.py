from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="books_demo")

@app.get("/books", response_model=list[schemas.Book])
def get_books(db: Session = Depends(get_db)):
    books = db.query(models.Book).all()
    return books
