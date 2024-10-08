import re
import socket
import ssl
from urllib.request import Request

from Constants import Constants
from WebScraper import WebScraper


class TLSHTMLRequester(WebScraper):
    def __init__(self, host: str = Constants.HOST, port: int = Constants.PORT):
        super().__init__()
        self.port = port
        self.host = host

    def create_request(self, custom_url: str = Constants.URL_WEBSITE, custom_headers=Constants.HEADERS) -> str:
        # Add to request url
        request = f"GET {custom_url} HTTP/1.1\r\n"
        # Add host to request url
        request += f"Host: {Constants.HOST}\r\n"
        # Add headers to request url
        for header, value in custom_headers.items():
            request += f"{header}: {value}\r\n"
        request += "\r\n"
        return request

    def send_request(self) -> str:
        tcp_ip_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_context = ssl.create_default_context()
        secure_tcp_ip_socket = ssl_context.wrap_socket(tcp_ip_sock, server_hostname=self.host)
        secure_tcp_ip_socket.connect((self.host, self.port))
        get_request = self.create_request(Constants.URL_WEBSITE, Constants.HEADERS)
        secure_tcp_ip_socket.send(get_request.encode())

        response = b""
        while True:
            chunk_data = secure_tcp_ip_socket.recv(2048)
            if len(chunk_data) == 5:
                break
            response += chunk_data

        secure_tcp_ip_socket.close()

        header, _, body = response.partition(b'\r\n\r\n')
        return body.decode()

    def get_html_from_url(self, request: str = None) -> str:
        return self.send_request()
