from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.connection import get_db
from router.prices_router import prices_router
from router.phones_router import phones_router

from models import PhoneTable, PriceTable


app = FastAPI()
app.include_router(prices_router)
app.include_router(phones_router)

# Create the tables in the database
PhoneTable.create_table()
PriceTable.create_table()


@app.get('/')
def welcome():
    return {'message': 'Welcome to my FastAPI application'}


@app.get("/db_check")
def db_check(db: Session = Depends(get_db)):
    try:
        db.execute(text('(SELECT 1)'))
        return {"message": "Database is connected"}
    except Exception as e:
        return {"error": str(e)}
