import json
from io import BytesIO

from .._http import HTTPResponse


class HTMLResponse(HTTPResponse):
    def __init__(self, html_file, **kwargs):
        self.html_file = html_file
        with open(html_file, 'r') as f:
            super().__init__(
                f.read(), *kwargs
            )

    def read(self):
        self.wfile = BytesIO()
        self.ready_response()
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        with open(self.html_file, 'r') as f:
            self.content = f.read().encode()
        self.ready_content()
        self.wfile.seek(0)
        return self.wfile.read()

class JSONResponse(HTTPResponse):
    def __init__(self, document, **kwargs):
        if isinstance(document, str):
            try:
                json.loads(document)
            except Exception as e:
                self.json = json.dumps({"error": str(e)})
            else:
                self.json = document
        elif isinstance(document, dict) or isinstance(document, list):
            self.json = json.dumps(document)
        else:
            raise ValueError("Document passed is not valid of type")

        super().__init__(
            self.json, *kwargs
        )

    def read(self):
        self.wfile = BytesIO()
        self.ready_response()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.ready_content()
        self.wfile.seek(0)
        return self.wfile.read()
