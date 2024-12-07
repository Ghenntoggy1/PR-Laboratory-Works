from threading import Thread

import uvicorn
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
import socket
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.connection import get_db
from router.prices_router import prices_router
from router.phones_router import phones_router
from models import PhoneTable, PriceTable
#
# from .database.connection import get_db
# from .router.prices_router import prices_router
# from .router.phones_router import phones_router
# from .models import PhoneTable, PriceTable

# IF RUN FROM PYCHARM
load_dotenv(".env")
HTTP_SERVER_GLOBAL_PORT = int(os.getenv("HTTP_SERVER_GLOBAL_PORT"))
UDP_SERVER_GLOBAL_PORT = int(os.getenv("UDP_SERVER_GLOBAL_PORT"))
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


def start_http_server(port: int):
    # uvicorn.run("Laboratory_Work_3_RAFT_RabbitMQ.Prerequisites.HTTPWebServer.run_web_server:app", host="0.0.0.0", port=port)
    uvicorn.run("RaftNode:app", host="0.0.0.0", port=port)

def start_udp_server(udp_port: int):
    # Create a UDP socket
    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to the address and port
    udp_server.bind(('0.0.0.0', udp_port))
    print(f"UDP Server listening on port {udp_port}...")
