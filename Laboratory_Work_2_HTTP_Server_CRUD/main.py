import asyncio
from threading import Thread

import uvicorn

from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy import text
from sqlalchemy.orm import Session

from database.connection import get_db
from router.prices_router import prices_router
from router.phones_router import phones_router
from models import PhoneTable, PriceTable
from Websocket import websocket_server


app = FastAPI()
app.include_router(prices_router)
app.include_router(phones_router)

# Create the tables in the database
PhoneTable.create_table()
PriceTable.create_table()

app.mount('/Websocket', StaticFiles(directory='Websocket', html=True), name='Websocket')


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


@app.get("/client")
def get_chat_page():
    with open("Websocket/index.html") as f:
        return HTMLResponse(content=f.read())


def start_websocket_server():
    asyncio.run(websocket_server.start_server())


def start_http_server():
    # uvicorn.run("main:app", host="localhost", port=8000)
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


if __name__ == "__main__":
    # Separate threads for websocket and http servers
    websocket_thread = Thread(target=start_websocket_server)
    http_thread = Thread(target=start_http_server)

    # Start the threads
    websocket_thread.start()
    http_thread.start()

    # Wait for the threads to finish
    websocket_thread.join()
    http_thread.join()
