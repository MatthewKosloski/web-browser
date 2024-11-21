from constants import WINDOW_HEIGHT
from css.style_computer import StyleComputer
from hypertext.parser import HTMLParser
from layout.document_layout_node import DocumentLayoutNode
from scrollbar import Scrollbar

class Tab:
    def __init__(self, canvas):
        self.scrollbar = None
        self.canvas = canvas
        self.display_list = []
        self.scrollbar_display_list = []
        self.url = None

    def load(self, url):
        self.scrollbar = None
        self.display_list = []
        self.url = url

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
        self.scrollbar = Scrollbar(self.document.height)

        # From the layout tree, produce a linear list of draw commands.
        self.paint(self.document, self.display_list)

        print("Draw commands:")
        for command in self.display_list:
            print(command)

    def draw(self, canvas, e = None):
        # Draw the scrollbar.
        scroll_cmd = self.scrollbar.paint(e)        
        if scroll_cmd is not None:
            scroll_cmd.execute(0, canvas)

        # Draw the web page.
        for command in self.display_list:
            if command.top > self.scrollbar.scroll + WINDOW_HEIGHT: continue
            if command.bottom < self.scrollbar.scroll: continue
            command.execute(self.scrollbar.scroll, canvas)

    def paint(self, layout_object, display_list):
        self.display_list.extend(layout_object.paint())

        for child in layout_object.children:
            self.paint(child, display_list)

    def scroll_down(self, e = None):
        if self.scrollbar is not None:
            self.scrollbar.scroll_down(e)

    def scroll_up(self, e = None):
        if self.scrollbar is not None:
            self.scrollbar.scroll_up(e)

    def log_tree(self, node, indent=0):
        print(" " * indent, node)
        for child in node.children:
            self.log_tree(child, indent + 4)