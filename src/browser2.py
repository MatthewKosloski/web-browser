import tkinter

from css.parser import CSSParser
from html2.nodes import Element
from html2.parser import HTMLParser
from layout.document_layout_node import DocumentLayoutNode
from scrollbar2 import Scrollbar
from url.url import Url

class BrowserConfig:
    def __init__(self, width, height, hstep, vstep):
        self.width = width
        self.height = height
        self.hstep = hstep
        self.vstep = vstep

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
        self.draw(e)

    def handle_event_up(self, e):
        if self.scrollbar is not None:
            self.scrollbar.scroll_up(e)
        self.draw(e)

    def print_tree(self, node, indent=0):
        print(" " * indent, node)
        for child in node.children:
            self.print_tree(child, indent + 4)


    def load(self, url):
        body = url.request()
        config = BrowserConfig(self.width, self.height, self.hstep, self.vstep)
        nodes = HTMLParser(body).parse()

        self.style(nodes)
        
        print("HTML tree:")
        self.print_tree(nodes)

        self.document = DocumentLayoutNode(config, nodes)
        self.document.layout()

        self.scrollbar = Scrollbar(
            canvas=self.canvas,
            window_width=self.width,
            window_height=self.height,
            vstep=self.vstep,
            max_y=self.document.height)
                
        print("Layout tree:")
        self.print_tree(self.document)
        
        self.display_list = []
        self.paint_tree(self.document, self.display_list)

        print("Draw commands:")
        print(self.display_list)

        self.draw()

    def to_screen_coordinate(self, page_coordinate):
        page_x, page_y = page_coordinate
        screen_x, screen_y = (page_x, page_y - self.scrollbar.scroll)

        return (screen_x, screen_y)

    def draw(self, e = None):
        self.canvas.delete("all")
        self.scrollbar.draw(e)

        for command in self.display_list:
            if command.top > self.scrollbar.scroll + self.height: continue
            if command.bottom < self.scrollbar.scroll: continue
            command.execute(self.scrollbar.scroll, self.canvas)

    def paint_tree(self, layout_object, display_list):
        display_list.extend(layout_object.paint())

        for child in layout_object.children:
            self.paint_tree(child, display_list)

    def style(self, node):
        node.style = {}

        if isinstance(node, Element) and "style" in node.attributes:
            pairs = CSSParser(node.attributes["style"]).body()

            for property, value in pairs.items():
                node.style[property] = value

        for child in node.children:
            self.style(child)

if __name__ == "__main__":
    import sys
    url = sys.argv[1]
    Browser().load(Url(url))
    tkinter.mainloop()