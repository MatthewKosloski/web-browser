from chrome.scrollbar import Scrollbar
from constants import WINDOW_HEIGHT
from css.style_computer import StyleComputer
from hypertext.nodes import Text
from hypertext.parser import HTMLParser
from layout.document_layout_node import DocumentLayoutNode

class Tab:
    def __init__(self, browser):
        self.scrollbar = None
        self.browser = browser
        self.display_list = []
        self.scrollbar_display_list = []
        self.url = None
        self.height = WINDOW_HEIGHT - browser.chrome.bottom

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

        # Create a scrollbar.
        self.scrollbar = Scrollbar(self)

        # From the layout tree, produce a linear list of draw commands.
        self.paint(self.document, self.display_list)

        print("Draw commands:")
        for command in self.display_list:
            print(command)

    def draw(self, e = None):
        # Draw the scrollbar.
        scroll_cmd = self.scrollbar.paint(e)        
        if scroll_cmd is not None:
            scroll_cmd.execute(self.browser.canvas)

        # Draw the web page.
        for command in self.display_list:
            if command.rect.top > self.scrollbar.scroll + WINDOW_HEIGHT: continue
            if command.rect.bottom < self.scrollbar.scroll: continue
            command.execute(self.browser.canvas, self.scrollbar.scroll - self.browser.chrome.bottom)

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

    def click(self, x, y):
        # Convert the screen coordinates to page coordinates.
        y += self.scrollbar.scroll

        # Perform a hit test. Get the list of layout objects that have been clicked.
        tree = self.tree_to_list(self.document, [])
        objs = [obj for obj in tree
            if obj.x <= x < obj.x + obj.width
            and obj.y <= y < obj.y + obj.height]
        
        # Early return if no layout object was clicked on.
        if not objs: return

        # The most specific node that was clicked is the last element in the hit test.
        elt = objs[-1].node

        while elt:
            if isinstance(elt, Text):
                pass
            elif elt.tag == "a" and "href" in elt.attributes:
                # A link element was clicked, so extract the URL and load it.
                url = self.url.resolve(elt.attributes["href"])
                self.load(url)
                self.draw()
            elt = elt.parent

    def tree_to_list(self, tree, list):
        list.append(tree)
        for child in tree.children:
            self.tree_to_list(child, list)
        return list

    def log_tree(self, node, indent=0):
        print(" " * indent, node)
        for child in node.children:
            self.log_tree(child, indent + 4)