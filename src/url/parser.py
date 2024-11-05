class UrlParser:

    @staticmethod
    def parse(url):
        scheme, url = url.split("://", 1)

        # # Add "/" suffix.
        # if url[-1] != "/":
        #     url += "/"

        # Ensure scheme is supported.
        supported_schemes = ["file", "http", "https"]
        assert scheme in supported_schemes

        if scheme in ["http", "https"]:
            host, url = url.split("/", 1)
            path = "/" + url
        else:
            host = ''
            path = url

        # Parse port.
        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)

        if scheme == "http":
            port = 80
        elif scheme == "https":
            port = 443 
        else:
            port = None

        # Remove leading forward slash in front of a file path.
        if scheme == "file" and path[0] == "/":
            path = path[1:]

        if host == "":
            host = None
        if path == "":
            path = None

        result = {
            "host": host,
            "path": path,
            "port": port,
            "scheme": scheme,
        }
        return result
    