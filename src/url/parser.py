from typing import Dict, Optional, Union

class UrlParser:

    @staticmethod
    def parse(url: str) -> Dict[str, Optional[Union[str, int]]]:

        if "://" in url:
            scheme, url = url.split("://", 1)
        else:
            scheme = 'http'

        # # Add "/" suffix.
        # if url[-1] != "/":
        #     url += "/"

        # Ensure scheme is supported.
        supported_schemes = ["file", "http", "https"]
        assert scheme in supported_schemes

        if scheme in ["http", "https"]:
            if "/" in url:
                host, url = url.split("/", 1)
                path = "/" + url
            else:
                host = url
                path = "/"
        else:
            host = ''
            path = url

        # Parse port.
        if scheme == "http":
            port = 80
        elif scheme == "https":
            port = 443 
        else:
            port = None

        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)


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
    