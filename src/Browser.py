import tkinter

from BrowserConfig import BrowserConfig
from DocumentLayout import DocumentLayout
from HTMLParser import HTMLParser
from Scrollbar import Scrollbar
from Url import Url

class Browser:

    def __init__(self, width = 800, height = 600, hstep = 13, vstep = 18):
        self.width = width
        self.height = height
        self.hstep = hstep
        self.vstep = vstep
        self.scrollbar = None
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=self.width,
            height=self.height
        )
        self.canvas.pack()

        # Bind events to event handlers.
        self.window.bind("<Down>", self.handle_event_down)
        self.window.bind("<Up>", self.handle_event_up)

    def handle_event_down(self, e):
        if self.scrollbar is not None:
            self.scrollbar.scroll_down(e)

        # Erase and redraw the canvas.
        self.canvas.delete("all")
        self.draw(e)

    def handle_event_up(self, e):
        if self.scrollbar is not None:
            self.scrollbar.scroll_up(e)

        # Erase and redraw the canvas.
        self.canvas.delete("all")
        self.draw(e)

    def load(self, url):
        body = url.request()
        config = BrowserConfig(self.width, self.height, self.hstep, self.vstep)
        nodes = HTMLParser(body).parse()
        self.document = DocumentLayout(config, nodes)
        self.document.layout()
        self.display_list = []
        self.paint_tree(self.document, self.display_list)
        self.scrollbar = Scrollbar(
            canvas=self.canvas,
            window_width=self.width,
            window_height=self.height,
            vstep=self.vstep,
            max_y=self.document.height)
        self.draw()

    def to_screen_coordinate(self, page_coordinate):
        page_x, page_y = page_coordinate
        screen_x, screen_y = (page_x, page_y - self.scrollbar.scroll)

        return (screen_x, screen_y)

    def draw(self, e = None):
        self.scrollbar.draw(e)

        for page_x, page_y, word, font in self.display_list:

            # Skip drawing characters that are offscreen.
            if page_y > self.scrollbar.scroll + self.height: continue
            if page_y + self.vstep < self.scrollbar.scroll: continue

            screen_x, screen_y = self.to_screen_coordinate((page_x, page_y))
            self.canvas.create_text(screen_x, screen_y, text=word, font=font, anchor='nw')

    def paint_tree(self, layout_objects, display_list):
        display_list.extend(layout_objects.paint())

        for child in layout_objects.children:
            self.paint_tree(child, display_list)

if __name__ == "__main__":
    import sys
    url = sys.argv[1]
    Browser().load(Url(url))
    tkinter.mainloop()