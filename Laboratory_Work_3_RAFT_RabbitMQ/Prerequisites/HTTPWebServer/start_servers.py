import time
from threading import Thread

from RaftNode import RaftNode

import os
from dotenv import load_dotenv


load_dotenv(".env")
HTTP_SERVER_GLOBAL_PORT = int(os.getenv("HTTP_SERVER_GLOBAL_PORT"))
UDP_SERVER_GLOBAL_PORT = int(os.getenv("UDP_SERVER_GLOBAL_PORT"))

if __name__ == "__main__":
    raft_nodes = []
    for i in range(3):
        print(f"Initializing RaftNode with UDP port: {UDP_SERVER_GLOBAL_PORT + i}")
        raft_nodes.append(
            RaftNode('127.0.0.1', HTTP_SERVER_GLOBAL_PORT + i, '127.0.0.1', UDP_SERVER_GLOBAL_PORT + i))

    for i in range(3):
        raft_nodes[i].add_new_peers([raft_nodes[j] for j in range(3) if j != i])

    threads = []
    for i in range(3):
        http_thread = Thread(target=raft_nodes[i].start_http_server)
        udp_thread = Thread(target=raft_nodes[i].start_udp_server)

        http_thread.start()
        udp_thread.start()

        threads.append(http_thread)
        threads.append(udp_thread)

    for thread in threads:
        thread.join()
