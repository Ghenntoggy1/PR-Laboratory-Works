import random
import socket
import threading
import time
from threading import Lock, Semaphore
from signal import signal, SIGINT

SHARED_RESOURCE = 'shared_resource.txt'
HOST = "0.0.0.0"
PORT = 1000
ALLOWED_CONNECTIONS = 10

# Mutex for exclusive access to the shared resource
mutex = Lock()
# Semaphore to prioritize write operations
# write_semaphore = Semaphore(1)
write_count = 0

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def start_tcp_server():
    server_socket.bind((HOST, PORT))
    server_socket.listen(ALLOWED_CONNECTIONS)
    print(f"Server is listening on {HOST}:{PORT}")


def stop_tcp_server(signum, frame):
    print("\nShutting down the server...")
    server_socket.close()
    exit(0)


def handle_client_connection(client_socket):
    global write_count
    try:
        request = client_socket.recv(1024).decode('utf-8')
        print(f"Received request: {request} from {client_socket.getpeername()}\n")

        command, *args = request.split(' ', 1)
        print("Write count:", write_count, "\n")

        if command == "write" and args:
            write_count += 1
            print("INCREMENT WRITE COUNT:", write_count)

            message = args[0]
            tm = random.randint(1, 7)

            print(f"WRITE THREAD {client_socket.getpeername()}: Sleeping for {tm} seconds...")
            time.sleep(tm)
            print(f"WRITE THREAD {client_socket.getpeername()}: Woke up after {tm} seconds. \n")

            # Acquire write priority
            with mutex:  # Lock resource for writing
                with open(SHARED_RESOURCE, 'a') as file:
                    file.write(message + '\n')
                response = f"{client_socket.getpeername()} wrote message {message} to file.\n"

            write_count -= 1
            print("DECREMENT WRITE COUNT:", write_count)

        elif command == "read":
            tm = random.randint(1, 7)
            print(f"READ THREAD {client_socket.getpeername()}: Sleeping for {tm} seconds...")
            time.sleep(tm)
            print(f"READ THREAD {client_socket.getpeername()}: Woke up after {tm} seconds.\n")

            while write_count > 0:
                print(f"{client_socket.getpeername()} Waiting for write threads ({write_count}) to finish...\n")
                time.sleep(0.1)

            print(f"No more write threads. {client_socket.getpeername()} reading the file...\n")
            with mutex:  # Lock resource for reading
                with open(SHARED_RESOURCE, 'r') as file:
                    content = file.read()
                response = "READ -\n" + content + "- END READ"
        else:
            response = "Invalid command."

        client_socket.sendall(response.encode('utf-8'))
    finally:
        client_socket.close()


if __name__ == "__main__":
    signal(SIGINT, stop_tcp_server)
    start_tcp_server()
    list_threads = []
    while True:
        client_socket, address = server_socket.accept()
        print(f"Accepted connection from {address}")
        client_handler = threading.Thread(target=handle_client_connection, args=(client_socket,))
        client_handler.start()
        list_threads.append(client_handler)
        # if len(list_threads) == 5:
        #     break

    # for thread in list_threads:
    #     thread.start()
    #
    # for thread in list_threads:
    #     thread.join()
