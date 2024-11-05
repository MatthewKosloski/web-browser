import tkinter
import os

from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from css.parser import CSSParser
from hypertext.nodes import Element
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
            height=WINDOW_HEIGHT
        )
        self.canvas.pack()

        # Bind events to event handlers.
        self.window.bind("<Down>", self.handle_event_down)
        self.window.bind("<Up>", self.handle_event_up)

    def tree_to_list(self, tree, list):
        list.append(tree)
        for child in tree.children:
            self.tree_to_list(child, list)
        return list

    def load(self, url):
        # Get HTML document, either from disk or the internet.
        body = url.request()

        # Parse the HTML document, returning a tree of nodes.
        nodes = HTMLParser(body).parse()
        
        print("HTML tree:")
        self.log_tree(nodes)

        # Get user agent default styles.
        default_stylesheet_path = os.path.join(os.path.dirname(__file__), "css/browser.css")
        default_stylesheet_content = open(default_stylesheet_path).read()
        rules = CSSParser(default_stylesheet_content).parse().copy()

        # Grab the URL of each linked style sheet.
        node_list = self.tree_to_list(nodes, [])
        links = []
        for node in node_list:
            if isinstance(node, Element) \
            and node.tag == "link" \
            and node.attributes.get("rel") == "stylesheet" \
            and "href" in node.attributes:
                links.append(node.attributes["href"])
        
        # Include CSS rules from each linked style sheet.
        for link in links:
            style_url = url.resolve(link)
            try:
                body = style_url.request()
            except:
                # Ignore stylesheets that fail to download.
                continue

            rules.extend(CSSParser(body).parse())

        self.style(nodes, rules)

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
        print(self.display_list)

        # Execute each draw command.
        self.draw()

    def style(self, node, rules):
        node.style = {}

        for selector, body in rules:
            if not selector.matches(node): continue
            for property, value in body.items():
                node.style[property] = value

        # Parse the style attribute after the rules.
        # The style attribute has higher specificity.
        if isinstance(node, Element) and "style" in node.attributes:
            pairs = CSSParser(node.attributes["style"]).body()

            for property, value in pairs.items():
                node.style[property] = value

        for child in node.children:
            self.style(child, rules)

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

    def to_screen_coordinate(self, page_coordinate):
        page_x, page_y = page_coordinate
        screen_x, screen_y = (page_x, page_y - self.scrollbar.scroll)

        return (screen_x, screen_y)

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