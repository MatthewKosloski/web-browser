import tkinter

from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from css.style_computer import StyleComputer
from hypertext.parser import HTMLParser
from layout.document_layout_node import DocumentLayoutNode
from scrollbar import Scrollbar
from url.url import Url

class Browser:
    def __init__(self):
        self.scrollbar = None
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg="white")
        self.canvas.pack()

        # Bind events to event handlers.
        self.window.bind("<Down>", self.handle_event_down)
        self.window.bind("<Up>", self.handle_event_up)

    def load(self, url):
        # Get HTML document, either from disk or the internet.
        body = url.request()

        # Parse the HTML document, returning a tree of nodes.
        nodes = HTMLParser(body).parse()
        
        print("HTML tree:")
        self.log_tree(nodes)

        # Apply user agent, linked style sheet, and inline style rules
        # to each element.
        style_computer = StyleComputer(nodes, url)
        style_computer.compute_style(nodes)

        # From the HTML tree, produce a layout tree with a root DocumentLayoutNode.
        self.document = DocumentLayoutNode(nodes)
        self.document.layout()

        print("Layout tree:")
        self.log_tree(self.document)

        # Create a scrollbar using the height of the root node of the layout tree.
        self.scrollbar = Scrollbar(self.canvas, self.document.height)
        
        # From the layout tree, produce a linear list of draw commands.
        self.display_list = []
        self.paint(self.document, self.display_list)

        print("Draw commands:")
        for command in self.display_list:
            print(command)

        # Execute each draw command.
        self.draw()

    def paint(self, layout_object, display_list):
        display_list.extend(layout_object.paint())

        for child in layout_object.children:
            self.paint(child, display_list)

    def draw(self, e = None):
        self.canvas.delete("all")
        self.scrollbar.draw(e)

        for command in self.display_list:
            if command.top > self.scrollbar.scroll + WINDOW_HEIGHT: continue
            if command.bottom < self.scrollbar.scroll: continue
            command.execute(self.scrollbar.scroll, self.canvas)

    def handle_event_down(self, e):
        if self.scrollbar is not None:
            self.scrollbar.scroll_down(e)
        self.draw(e)

    def handle_event_up(self, e):
        if self.scrollbar is not None:
            self.scrollbar.scroll_up(e)
        self.draw(e)

    def log_tree(self, node, indent=0):
        print(" " * indent, node)
        for child in node.children:
            self.log_tree(child, indent + 4)

if __name__ == "__main__":
    import sys
    url = sys.argv[1]
    Browser().load(Url(url))
    tkinter.mainloop()