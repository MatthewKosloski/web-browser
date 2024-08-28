import socket
import ssl
import tkinter
import math

class URLParser:

    @staticmethod
    def parse(url):
        scheme, url = url.split("://", 1)

        # # Add "/" suffix.
        # if url[-1] != "/":
        #     url += "/"

        # Ensure scheme is supported.
        supported_schemes = ["file", "http", "https"]
        assert scheme in supported_schemes

        host, url = url.split("/", 1)
        path = "/" + url

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
        if scheme == "file":
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
    
class URL:

    def __init__(self, url):
        url_parts = URLParser.parse(url)
        self.host = url_parts["host"]
        self.path = url_parts["path"]
        self.port = url_parts["port"]
        self.scheme = url_parts["scheme"]

    def read_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                content = file.read()
                return content
        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return None

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

class Browser:

    def __init__(self, width = 800, height = 600, hstep = 13, vstep = 18):
        self.width = width
        self.height = height
        self.hstep = hstep
        self.vstep = vstep
        self.scroll = 0
        self.scrollbar_color = "blue"
        self.scrollbar_width = 15
        self.scrollbar_y0 = None
        self.scrollbar_y1 = None
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=self.width,
            height=self.height
        )
        self.canvas.pack()

        # Bind events to event handlers.
        self.window.bind("<Down>", self.scroll_down)
        self.window.bind("<Up>", self.scroll_up)

    def load(self, url):
        body = url.request()
        text = lex(body)
        self.display_list = layout(text, self.width, self.hstep, self.vstep)
        self.scroll_step = self.calculate_scroll_step()
        self.draw()

    def to_screen_coordinate(self, page_coordinate):
        page_x, page_y = page_coordinate
        screen_x, screen_y = (page_x, page_y - self.scroll)

        return (screen_x, screen_y)
    
    def calculate_scroll_distance(self):
        """
        Calculates the scrollable distance.
        """
        max_page_y = self.display_list[-1][1]

        if max_page_y + self.vstep > self.height:
            distance = max_page_y + self.vstep - self.height
        else:
            # All page contents are within the viewport, therefore,
            # the scrollable distance is zero.
            distance = 0

        return distance
    
    def get_scroll_steps(self):
        """
        Returns the number of scroll steps.
        """
        scroll_distance = self.calculate_scroll_distance()

        if self.scroll_step > 0:
            num_steps = int(scroll_distance / self.scroll_step)
        else:
            num_steps = 0

        return num_steps

    def calculate_scroll_step(self):
        """
        Calculates the scroll step. That is, by how many vertical points
        we want to move the scroll bar down for each scroll event.
        """

        # We don't want the scroll step to exceed half the height of the window.
        max_scroll_step = math.floor(self.height / 2)

        scroll_distance = self.calculate_scroll_distance()

        if scroll_distance > max_scroll_step:
            num_steps = math.floor(scroll_distance / max_scroll_step)
        else:
            # The maximum scrollable distance is less than half
            # the height of the window, therefore, we can complete
            # the scroll in a single step.
            num_steps = 1

        # Find the required number of scroll steps such that
        # the step amount does not exceed half the height of the window.
        while (num_steps > 0 and scroll_distance / num_steps > max_scroll_step):
            num_steps += 1

        # Calculate the required scroll step to complete num_steps of scroll.
        if num_steps > 0:
            scroll_step = scroll_distance / num_steps
        else:
            scroll_step = 0

        return scroll_step
    
    def calculate_scrollbar_height(self):
        """
        Calculates the scrollbar height. If the maximum scrollable distance
        is zero, then the scrollbar height is zero.
        """

        scroll_distance = self.calculate_scroll_distance()

        if scroll_distance > 0:

            if scroll_distance <= self.height:
                visible_content_percentage = (self.height - scroll_distance) / self.height
            else:
                visible_content_percentage = self.height / scroll_distance
                
            scrollbar_height = visible_content_percentage * self.height
        else:
            # There is no distance to scroll, therefore, there is no scrollbar.
            scrollbar_height = 0

        return scrollbar_height
    
    def draw_scrollbar(self, e = None):
        scrollbar_height = self.calculate_scrollbar_height()

        # We don't need to draw a scrollbar.
        if scrollbar_height <= 0:
            return

        y0_lower_limit = 0
        y0_upper_limit = self.height - scrollbar_height
        y1_lower_limit = scrollbar_height
        y1_upper_limit = self.height

        scroll_steps = self.get_scroll_steps()
        y0_step = (y0_upper_limit - y0_lower_limit) / scroll_steps
        y1_step = (y1_upper_limit - y1_lower_limit) / scroll_steps

        if self.scrollbar_y0 is None:
            self.scrollbar_y0 = 0
        if e is not None and e.keysym == "Down":
            self.scrollbar_y0 += y0_step
        elif e is not None and e.keysym == "Up":
            self.scrollbar_y0 -= y0_step

        
        if self.scrollbar_y1 is None:
            self.scrollbar_y1 = scrollbar_height
        elif e is not None and e.keysym == "Down":
            self.scrollbar_y1 += y1_step
        elif e is not None and e.keysym == "Up":
            self.scrollbar_y1 -= y1_step

        # Prevent y0 from exiting boundary.
        if self.scrollbar_y0 >= y0_upper_limit:
            self.scrollbar_y0 = y0_upper_limit
        elif self.scrollbar_y0 <= y0_lower_limit:
            self.scrollbar_y0 = y0_lower_limit

        # Prevent y1 from exiting boundary.
        if self.scrollbar_y1 >= y1_upper_limit:
            self.scrollbar_y1 = y1_upper_limit
        elif self.scrollbar_y1 <= y1_lower_limit:
            self.scrollbar_y1 = y1_lower_limit

        x0, y0 = (self.width - self.scrollbar_width, self.scrollbar_y0)
        x1, y1 = (self.width, self.scrollbar_y1)

        self.canvas.create_rectangle(x0, y0, x1, y1, fill = self.scrollbar_color, width = 0)

    def draw(self, e = None):
        self.draw_scrollbar(e)

        for page_x, page_y, c in self.display_list:

            # Skip drawing characters that are offscreen.
            if page_y > self.scroll + self.height: continue
            if page_y + self.vstep < self.scroll: continue

            screen_x, screen_y = self.to_screen_coordinate((page_x, page_y))
            self.canvas.create_text(screen_x, screen_y, text=c)

    def scroll_down(self, e):
        # Check if we have a scrollbar. If not, then don't do anything.
        scrollbar_height = self.calculate_scrollbar_height()
        if scrollbar_height <= 0:
            return

        # Do not scroll down past the page.
        max_page_y = self.display_list[-1][1]
        max_scroll = max_page_y + self.vstep - self.height
        if self.scroll + self.scroll_step >= max_scroll:
            self.scroll = max_scroll
        else:
            self.scroll += self.scroll_step

        # Erase and redraw the canvas.
        self.canvas.delete("all")
        self.draw(e)

    def scroll_up(self, e):
        # Check if we have a scrollbar. If not, then don't do anything.
        scrollbar_height = self.calculate_scrollbar_height()
        if scrollbar_height <= 0:
            return

        # Do not scroll up past the page.
        min_scroll = 0
        if self.scroll - self.scroll_step <= min_scroll:
            self.scroll = min_scroll
        else:
            self.scroll -= self.scroll_step

        # Erase and redraw the canvas.
        self.canvas.delete("all")
        self.draw(e)

'''
  Computes and stores the position of each character, storing
  it in a display list. This function operates using page coordinates.
'''
def layout(text, window_width, hstep = 13, vstep = 18):
    display_list = []
    cursor_x, cursor_y = hstep, vstep

    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += hstep
        # Wrap the text once we reach the edge of the screen.
        # The ICU Library, used by both Firefox and Chrome, uses
        # dynamic programming to guess phase boundaries based on
        # a word frequency table.
        # https://site.icu-project.org/
        # https://github.com/unicode-org/icu/blob/master/icu4c/source/data/brkitr/dictionaries/cjdict.txt
        if cursor_x >= window_width - hstep:
            cursor_y += vstep
            cursor_x = hstep

    return display_list

def lex(body):
    text = ""
    in_tag = False
    for c in body:
        if c == "<":
            in_tag = True
        elif c == ">":
            in_tag = False
        elif not in_tag:
            text += c
    return text

if __name__ == "__main__":
    import sys
    url = sys.argv[1]
    Browser().load(URL(url))
    tkinter.mainloop()