import socket
from urllib import parse
from typing import Dict

ENTRIES = [ 'Matt was here!' ]

def do_request(method: str, url: str, headers: Dict[str, str], body: str) -> None:
    if method == "GET" and url == "/":
        return "200 OK", show_comments()
    elif method == "POST" and url == "/add":
        params = form_decode(body)
        return "200 OK", add_entry(params)
    elif method == "GET" and url == "/comment.js":
        with open("comment.js") as f:
            return "200 OK", f.read()
    elif method == "GET" and url == "/comment.css":
        with open("comment.css") as f:
            return "200 OK", f.read()
    else:
        return "404 Not Found", not_found(url, method)
    
def form_decode(body: str) -> Dict[str, str]:
    params = {}
    for field in body.split("&"):
        name, value = field.split("=", 1)
        name = parse.unquote_plus(name)
        value = parse.unquote_plus(value)
        params[name] = value
    return params

def add_entry(params: Dict[str, str]) -> str:
    if 'guest' in params:
        ENTRIES.append(params['guest'])
    return show_comments()

def not_found(url: str, method: str) -> str:
    out = "<!doctype html>"
    out += "<h1>{} {} not found!</h1>".format(method, url)

    return out

def show_comments() -> str:
    out = "<!doctype html>"
    out += "<link rel=stylesheet href=comment.css>"

    for entry in ENTRIES:
        out += "<p>" + entry + "</p>"

    out += "<form action=add method=post>"
    out +=   "<p><input name=guest></p>"
    out +=   "<p><button>Sign the book!</button></p>"
    out += "</form>"

    out += "<strong></strong>"

    out += "<script src=/comment.js></script>"
    
    return out

def handle_connection(conx: socket.socket) -> None:
    # Read the request line.
    req = conx.makefile("b")
    reqline = req.readline().decode("utf8")
    method, url, version = reqline.split(" ", 2)
    assert method in ["GET", "POST"]

    # Read headers until a blank line.
    headers = {}
    while True:
        line = req.readline().decode("utf8")
        if line == '\r\n': break
        header, value = line.split(":", 1)
        headers[header.casefold()] = value.strip()

    # Read the body.
    if 'content-length' in headers:
        length = int(headers['content-length'])
        body = req.read(length).decode('utf8')
    else:
        body = None

    # Generate a web page in response.
    status, body = do_request(method, url, headers, body)

    # Send web page back to the client.
    response = "HTTP 1.0 {}\r\n".format(status)
    response += "Content-Length: {}\r\n".format(len(body.encode("utf8")))
    response += "\r\n" + body

    conx.send(response.encode("utf8"))
    conx.close()

s = socket.socket(
    family=socket.AF_INET,
    type=socket.SOCK_STREAM,
    proto=socket.IPPROTO_TCP)

# Allow port reuse if process crashes.
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Wait for a connection.
s.bind(('', 8000))

s.listen()

while True:
    conx, addr = s.accept()
    handle_connection(conx)
