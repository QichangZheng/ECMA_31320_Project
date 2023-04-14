import mimetypes
import pathlib
import re

from ._http import HTTPRequest, HTTPResponse


class StaticDeliverer():
    """ Static Deliverer
    A way to deliver static files (eg. images, js, etc.) without
    something nginx. This class is only designed to be used in debug
    environments. When deploying, use something like nginx to deliver
    static files.
    """
    def __init__(
            self, prefix=None, domain=r".*",
            src="./"):
        
        self.path = f"^/{prefix}/.*$" if prefix else "^/.*$"
        self.domain = domain
        self.src = src

        mimetypes.init()

    def __call__(self, request):
        req_file = pathlib.PurePath(
            self.src, re.sub(self.path.rstrip('.*$'), '', request.path)
        ).as_posix()

        if not pathlib.Path(req_file).is_file():
            return None

        with open(req_file, 'rb') as f:
            mime = mimetypes.guess_type(request.path)[0]

            if not mime:
                raise TypeError(f"Was unable to interpret mimetype of {req_file}")

            return HTTPResponse(
                f.read(), content_type=mime
            )
