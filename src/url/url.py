import socket
import ssl

from url.parser import UrlParser

class Url:
    '''
        Parses a URL and then attempts to request the content from it. If the
        host has an http scheme, then a HTTP 1.0 request is made to the host.
        If the host has a file scheme, then a read to disk is initiated.
    
        Supported schemes include:
          - http(s)
          - file
    '''

    def __init__(self, url):
        url_parts = UrlParser.parse(url)
        self.host = url_parts["host"]
        self.path = url_parts["path"]
        self.port = url_parts["port"]
        self.scheme = url_parts["scheme"]

    def request(self):

        # If the URL is to a file, then try to read the file contents.
        if self.scheme == "file":
            content = self.read_file(self.path)
            return content

        # Otherwise, try to connect to the web server.

        s = socket.socket(
            family=socket.AF_INET,
            # We can send arbitrary amounts of data with a stream.
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)

        s.connect((self.host, self.port))

        # It's important to use \r\n instead of \n.
        request = "GET {} HTTP/1.0\r\n".format(self.path)

        # It's important to put two newlines at the end,
        # otherwise the server will keep waiting for that
        # newline, and we'll keep waiting on its response.
        request += "Host: {}\r\n".format(self.host)
        request += "\r\n"

        # Convert the text into bytes and send the request.
        s.send(request.encode("utf8"))

        # Encode the response bytes into a UTF-8 string.
        # Hard-coding UTF-8 is not correct. Instead, we
        # should be looking at the charset declaration in
        # the Content-Type response header.
        response = s.makefile("r", encoding="utf8", newline="\r\n")

        statusline = response.readline()
        version, status, explanation = statusline.split(" ", 2)

        response_headers = {}
        while True:
            line = response.readline()
            if line == "\r\n": break
            header, value = line.split(":", 1)
            # We use casefold() instead of lower() because it works
            # better for more languages.
            response_headers[header.casefold()] = value.strip()

        assert "transfer-encoding" not in response_headers
        assert "content-encoding" not in response_headers

        content = response.read()
        s.close()

        return content
    

    def read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                return content
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return None