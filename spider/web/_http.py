import json
import email.message
import gzip
import http.client
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from io import BytesIO
from urllib import parse


PROTOCOL_VERSION = "HTTP/1.1"

class HTTPRequest:
    command: str
    path: str
    request_version: str
    headers: email.message.Message
    body: str
    client: tuple

    default_request_version = "HTTP/0.9"
    protocol_version = PROTOCOL_VERSION
    MessageClass = http.client.HTTPMessage

    def __new__(cls, *args, **kwargs):
        cls.parse_request = BaseHTTPRequestHandler.parse_request
        return super().__new__(cls)

    def __init__(self, request, client):
        self.rfile = BytesIO(request.encode())
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.expect_100 = False
        self.client = client
        self.parse_request()
        self.body = self.rfile.read()
    
    def __repr__(self) -> str:
        return f"{self.protocol_version} {self.path} {self.command} {self.client}"

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

    def handle_expect_100(self):
        self.expect_100 = True
        return True

    @property
    def params(self) -> dict:
        _path = parse.urlparse(self.path)
        return parse.parse_qs(_path.query, True)
    
    @property
    def body_json(self) -> dict:
        try:
            return json.loads(self.body)
        except:
            return None

class HTTPResponse:
    sys_version = "Python/" + sys.version.split()[0]
    server_version = "Spider/0.0.1"
    protocol_version = PROTOCOL_VERSION

    responses = {
        v: (v.phrase, v.description)
        for v in HTTPStatus.__members__.values()
    }

    def __new__(cls, *args, **kwargs):
        cls.send_response_only = BaseHTTPRequestHandler.send_response_only
        cls.send_header = BaseHTTPRequestHandler.send_header
        cls.flush_headers = BaseHTTPRequestHandler.flush_headers
        cls.end_headers = BaseHTTPRequestHandler.end_headers

        cls.version_string = BaseHTTPRequestHandler.version_string
        cls.date_time_string = BaseHTTPRequestHandler.date_time_string

        return super().__new__(cls)

    def __init__(self, response, code=200, version="HTTP/1.1", headers={},
            compress=True, compression_amount=5):

        self.response_code = code
        self.compress = compress
        self.compression_amount = compression_amount
        self.headers = headers

        # Validate HTTP version
        try:
            if not version.startswith('HTTP/'):
                raise ValueError
            base_version_number = version.split('/', 1)[1]
            version_number = base_version_number.split(".")
            if len(version_number) != 2:
                raise ValueError
            version_number = int(version_number[0]), int(version_number[1])
        except (ValueError, IndexError):
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                f"Bad request version ({version})")
            return False
        if version_number >= (1, 1) and self.protocol_version >= "HTTP/1.1":
            self.close_connection = False
        if version_number >= (2, 0):
            self.send_error(
                HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,
                f"Invalid HTTP version ({base_version_number})")
            return False
        self.request_version = version

        # Validate content type
        if isinstance(response, str):
            self.content = response.encode()
        elif isinstance(response, bytes):
            self.content = response
        else:
            raise ValueError("Content is not bytes-like or encodable")
    
    def send_response(self, code, message=None):
        self.send_response_only(code, message)
        self.send_header('Server', self.version_string())
        self.send_header('Date', self.date_time_string())

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message

    def ready_response(self):
        # Write the HTTP response
        self.send_response(self.response_code)
        
        # Add any custom headers and write
        for header in self.headers:
            self.send_header(header, self.headers[header])

        # If we're using compression, notify in header
        if self.compress:
            self.send_header("Content-Encoding", "gzip")

    def ready_content(self):
        # Write the content and compress if compression enabled
        if self.compress:
            self.wfile.write(gzip.compress(
                self.content, self.compression_amount
            ))
        else:
            self.wfile.write(self.content)

    def read(self):
        # Open a new BytesIO in memory
        self.wfile = BytesIO()

        self.ready_response()
        self.end_headers()
        self.ready_content()

        # Move the pointer back to start for reading
        self.wfile.seek(0)

        # Return the final response
        return self.wfile.read()
