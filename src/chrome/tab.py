from urllib import parse

from tkinter import Event
from typing import List, Optional

from chrome.scrollbar import Scrollbar
from constants import WINDOW_HEIGHT
from css.style_computer import StyleComputer
from hypertext.nodes import Element, Text, HTMLNode
from hypertext.parser import HTMLParser
from hypertext.utils import log_tree as log_html_tree
from javascript.JSContext import JSContext
from layout.document_layout_node import DocumentLayoutNode
from layout.layout_node import LayoutNode
from layout.utils import log_tree as log_layout_tree, tree_to_list
from url.url import Url

class Tab:
    def __init__(self, browser) -> None:
        self.scrollbar = None
        self.browser = browser
        self.display_list = []
        self.url = None
        self.height = WINDOW_HEIGHT - browser.chrome.bottom
        self.history: List[str] = []
        self.nodes = None
        self.style_computer = None
        self.focus = None
        self.js = None

    def load(self, url: Url, payload: Optional[str] = None) -> None:
        self.history.append(url)
        self.scrollbar = None
        self.display_list = []
        self.url = url

        # Initialize the JavaScript execution environment.
        self.js = JSContext()

        # Get HTML document, either from disk or the internet.
        body = url.request(payload)

        # Parse the HTML document, returning a tree of nodes.
        self.nodes = HTMLParser(body).parse()
        
        print("HTML tree:")
        log_html_tree(self.nodes)

        # Download stylesheets and initialize style computer.
        self.style_computer = StyleComputer(self.nodes, self.url)

        scripts = [node.attributes["src"] for node
            in tree_to_list(self.nodes, [])
            if isinstance(node, Element)
            and node.tag == "script"
            and "src" in node.attributes]
        
        for script in scripts:
            script_url = url.resolve(script)
            try:
                body = script_url.request()
            except:
                continue

            self.js.run(body)

        self.render()

    def render(self) -> None:
        '''
        Recompute style and layout, reinitialize scrollbar, and paint.
        '''

        self.display_list = []

        # Apply user agent, linked style sheet, and inline style rules
        # to each element.
        self.style_computer.compute_style(self.nodes)

        # From the HTML tree, produce a layout tree with a root DocumentLayoutNode.
        self.document = DocumentLayoutNode(self.nodes)
        self.document.layout()

        print("Layout tree:")
        log_layout_tree(self.document)

        # Create a scrollbar.
        self.scrollbar = Scrollbar(self)

        # From the layout tree, produce a linear list of draw commands.
        self.paint(self.document, self.display_list)

        print("Draw commands:")
        for command in self.display_list:
            print(command)

    def draw(self, e: Optional[Event] = None) -> None:
        # Draw the scrollbar.
        self.scrollbar.draw(e)

        # Draw the web page.
        for command in self.display_list:
            if command.rect.top > self.scrollbar.scroll + WINDOW_HEIGHT: continue
            if command.rect.bottom < self.scrollbar.scroll: continue
            command.execute(self.browser.canvas, self.scrollbar.scroll - self.browser.chrome.bottom)

    def paint(self, layout_object: LayoutNode, display_list: List[LayoutNode]) -> None:
        if layout_object.should_paint():
            self.display_list.extend(layout_object.paint())

        for child in layout_object.children:
            self.paint(child, display_list)

    def scroll_down(self) -> None:
        self.scrollbar.scroll_down()

    def scroll_up(self) -> None:
        self.scrollbar.scroll_up()

    def click(self, x: int, y: int) -> None:
        # Blur the tab.
        self.focus = None

        # Convert the screen coordinates to page coordinates.
        y += self.scrollbar.scroll

        # Perform a hit test. Get the list of layout objects that have been clicked.
        tree = tree_to_list(self.document, [])
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
            elif elt.tag == "input":
                elt.attributes["value"] = ""
                if self.focus:
                    self.focus.is_focused = False
                self.focus = elt
                elt.is_focused = True
                self.render()
            elif elt.tag == "button":
                # Find the nearest parent form and submit it.
                while elt:
                    if elt.tag == "form" and "action" in elt.attributes:
                        return self.submit_form(elt)
                    elt = elt.parent
            elt = elt.parent

    def submit_form(self, elt: HTMLNode) -> None:
        # Get all inputs of the form.
        inputs = [node for node in tree_to_list(elt, [])
            if isinstance(node, Element)
            and node.tag == "input"
            and "name" in node.attributes]
        body = ""

        for input in inputs:
            name = input.attributes["name"]
            value = input.attributes.get("value", "")

            # Percent encode name and value, replacing all special characters
            # with a percent sign followed by those characters' hex codes.
            name = parse.quote(name)
            value = parse.quote(value)
            body += "&" + name + "=" + value
        
        # Remove the extra &.
        body = body[1:]

        url = self.url.resolve(elt.attributes["action"])
        self.load(url, body)

    def go_back(self) -> None:
        if len(self.history) > 1:
            self.history.pop()
            back = self.history.pop()
            self.load(back)

    def keypress(self, char: str) -> None:
        if self.focus:
            self.focus.attributes["value"] += char
            self.render()