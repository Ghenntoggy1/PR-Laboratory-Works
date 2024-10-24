from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session


from database.connection import get_db, engine
from router.prices import prices_router

app = FastAPI()
app.include_router(prices_router)

from models import PhoneTable, PriceTable
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