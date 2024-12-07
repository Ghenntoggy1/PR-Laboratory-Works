import json
import random
import time
from enum import Enum
from threading import Thread, Timer

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


class RaftNodeStatus(Enum):
    FOLLOWER = 0
    CANDIDATE = 1
    LEADER = 2

class RaftNode:
    def __init__(self, http_server_host: str, http_server_port: int, udp_client_host: str, udp_client_port: int):
        self.http_server_host = http_server_host
        self.http_server_port = http_server_port
        self.udp_client_host = udp_client_host
        self.udp_client_port = udp_client_port

        self.udp_server: socket = None
        self.udp_client: socket = None

        self.state = RaftNodeStatus.FOLLOWER
        self.current_term = 0
        self.voted_for = None
        self.votes_received = 0
        self.is_leader = False
        self.heartbeat_interval = random.randint(3, 6) # 3-6 seconds
        self.election_timeout = random.randint(5, 10) # 5-10 seconds
        self.election_timer = None
        self.heartbeat_timer = None

        self.peers: list[RaftNode] = []

    def start_http_server(self):
        # uvicorn.run("Laboratory_Work_3_RAFT_RabbitMQ.Prerequisites.HTTPWebServer.run_web_server:app", host="0.0.0.0", port=port)
        # self.http_server_host_port = f"0.0.0.0:{port}"
        uvicorn.run("RaftNode:app", host=self.http_server_host, port=self.http_server_port)

    def start_udp_server(self):
        # Create a UDP socket
        udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Bind the socket to the address and port
        udp_client.bind((self.udp_client_host, self.udp_client_port))
        self.udp_client = udp_client

        listener_thread = Thread(target=self.listen_udp_messages)
        listener_thread.start()

        self.reset_election_timer()


    def listen_udp_messages(self):
        udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_server.bind((self.udp_client_host, self.udp_client_port + len(self.peers) + 1))
        print(f"UDP Server listening on port {udp_server.getsockname()[1]}...")
        self.udp_server = udp_server
        while True:
            try:
                data, address = udp_server.recvfrom(1024)
                print(f"Received message from {address}: {data.decode()}")
                message = json.loads(data.decode())
                print(f"Message: {message}")
                self.handle_message(message, address)
            except ConnectionError as e:
                print(f"Error: {e}")


    def handle_message(self, message: dict, address):
        print(f"Node {self.http_server_host}:{self.http_server_port} received message: {message}")
        if message['type'] == 'VOTE_REQUEST':
            print(f"Node {self.http_server_host}:{self.http_server_port} received vote request from {message['candidate']} for term {message['term']}")
            self.handle_vote_request(message, address)
        elif message['type'] == 'VOTE_RESPONSE':
            print(f"Node {self.http_server_host}:{self.http_server_port} received vote response for term {message['term']}")
            self.handle_vote_response(message)
        elif message['type'] == 'HEARTBEAT':
            print(f"Node {self.http_server_host}:{self.http_server_port} received heartbeat from {message['leader']} for term {message['term']}")
            self.handle_heartbeat(message)
        else:
            print(f"Node {self.http_server_host}:{self.http_server_port} received message: {message}")

    def handle_vote_request(self, message, address):
        print(f"Node {self.http_server_host}:{self.http_server_port} received vote request from {message['candidate']} for term {message['term']}")
        if (message['term'] > self.current_term) or \
                (message['term'] == self.current_term and not self.voted_for):
            self.state = RaftNodeStatus.FOLLOWER
            self.current_term = message['term']
            self.voted_for = message['candidate']
            self.reset_election_timer()

            response = {
                "type": "VOTE_RESPONSE",
                "term": self.current_term,
                "vote_granted": True,
            }
            print(f"Node {self.http_server_host}:{self.http_server_port} voted for {message['candidate']} for term {message['term']}")
            host, port = address
            self.udp_server.sendto(json.dumps(response).encode(), (host, int(port) + len(self.peers) + 1))
        else:
            response = {
                "type": "VOTE_RESPONSE",
                "term": self.current_term,
                "vote_granted": False,
            }
            print(f"Node {self.http_server_host}:{self.http_server_port} denied vote for {message['candidate']} for term {message['term']}")
            host, port = address
            self.udp_server.sendto(json.dumps(response).encode(), (host, int(port) + len(self.peers) + 1))

    def reset_election_timer(self):
        if self.election_timer:
            self.election_timer.cancel()
        random_timeout = random.randint(5, 10)
        print(f"Node {self.http_server_host}:{self.http_server_port} reset election timer - {random_timeout} seconds")
        self.election_timer = Timer(random_timeout, self.start_election)
        self.election_timer.start()

    def handle_vote_response(self, message):
        print(f"Node {self.http_server_host}:{self.http_server_port} received vote response for term {message['term']}")
        if message['term'] == self.current_term and message['vote_granted']:
            self.votes_received += 1
            if self.votes_received > len(self.peers) // 2:
                print(f"Node {self.http_server_host}:{self.http_server_port} became leader for term {self.current_term}")
                self.become_leader()

    def become_leader(self):
        self.state = RaftNodeStatus.LEADER
        self.is_leader = True
        print(f"Node {self.http_server_host}:{self.http_server_port} became leader for term {self.current_term}")
        self.start_heartbeat()

    def start_heartbeat(self):
        print(f"Node {self.http_server_host}:{self.http_server_port} started heartbeat")
        if self.heartbeat_timer:
            self.heartbeat_timer.cancel()
        self.heartbeat_timer = Timer(self.heartbeat_interval, self.send_heartbeat)
        self.heartbeat_timer.start()

    def send_heartbeat(self):
        for peer in self.peers:
            message = {
                'type': 'HEARTBEAT',
                'term': self.current_term,
                'leader': f"{self.http_server_host}:{self.http_server_port}"
            }
            host, port = peer.udp_client_host, peer.udp_client_port + len(self.peers) + 1
            print(f"Node {self.http_server_host}:{self.http_server_port} sending heartbeat to {peer} for term {self.current_term}")
            self.udp_client.sendto(json.dumps(message).encode(), (host, port))
        self.start_heartbeat()

    def start_election(self):
        self.state = RaftNodeStatus.CANDIDATE
        self.current_term += 1
        self.voted_for = f"{self.http_server_host}:{self.http_server_port}"
        self.votes_received = 1
        print(f"Node {self.http_server_host}:{self.http_server_port} started election for term {self.current_term}")

        for peer in self.peers:
            message = {
                'type': 'VOTE_REQUEST',
                'term': self.current_term,
                'candidate': f"{self.udp_client_host}:{self.udp_client_port}"
            }
            print(f"Node {self.http_server_host}:{self.http_server_port} sending vote request to {peer.http_server_host}:{peer.http_server_port} for term {self.current_term}")
            host, port = peer.udp_client_host, peer.udp_client_port

            addr = (host, port + len(self.peers) + 1)
            print(f"Sending message to {addr}")
            self.udp_client.sendto(json.dumps(message).encode(), addr)

    def handle_heartbeat(self, message: dict):
        print(f"Node {self.http_server_host}:{self.http_server_port} received heartbeat from {message['leader']} for term {message['term']}")
        if message['term'] >= self.current_term:
            self.state = RaftNodeStatus.FOLLOWER
            self.current_term = message['term']
            self.voted_for = None
            self.reset_election_timer()

    def add_new_peers(self, peers: list):
        for peer_host_port in peers:
            if peer_host_port not in self.peers:
                self.peers.append(peer_host_port)

    def is_leader(self):
        return self.is_leader == RaftNodeStatus.LEADER