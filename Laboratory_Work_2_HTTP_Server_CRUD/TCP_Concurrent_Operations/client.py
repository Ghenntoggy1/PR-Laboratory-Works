import socket
import time


def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect(('localhost', 1000))
        client_socket.sendall(command.encode('utf-8'))
        response = client_socket.recv(1024)
        print(f"Server response: {response.decode('utf-8')}")


if __name__ == "__main__":
    send_command(input("Enter command: "))
