from threading import Thread

import uvicorn

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles

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


def start_http_server():
    # uvicorn.run("main:app", host="localhost", port=8000)
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # Separate threads for websocket and http servers
    http_thread = Thread(target=start_http_server)

    # Start the threads
    http_thread.start()

    # Wait for the threads to finish
    http_thread.join()
