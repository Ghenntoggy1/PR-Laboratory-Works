from threading import Thread

from RaftNode import start_http_server, start_udp_server

import os
from dotenv import load_dotenv


load_dotenv(".env")
HTTP_SERVER_GLOBAL_PORT = int(os.getenv("HTTP_SERVER_GLOBAL_PORT"))
UDP_SERVER_GLOBAL_PORT = int(os.getenv("UDP_SERVER_GLOBAL_PORT"))

if __name__ == "__main__":
    threads = []
    for i in range(3):
        http_thread = Thread(target=start_http_server, args=(HTTP_SERVER_GLOBAL_PORT + i,))
        utp_thread = Thread(target=start_udp_server, args=(UDP_SERVER_GLOBAL_PORT + i,))

        http_thread.start()
        utp_thread.start()

        threads.append(http_thread)
        threads.append(utp_thread)

    for thread in threads:
        thread.join()
