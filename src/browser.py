import tkinter

from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from hypertext.nodes import Text
from chrome.tab import Tab
from url.url import Url

class Browser:

    def __init__(self):
        self.tabs = []
        self.active_tab = None
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
        self.window.bind("<Button-1>", self.handle_event_click)

    def new_tab(self, url):
        new_tab = Tab(self.canvas)
        new_tab.load(url)
        self.active_tab = new_tab
        self.tabs.append(new_tab)
        self.draw()

    def draw(self, e = None):
        self.canvas.delete("all")
        self.active_tab.draw(self.canvas, e)

    def handle_event_down(self, e):
        self.active_tab.scroll_down(e)
        self.draw(e)

    def handle_event_up(self, e):
        self.active_tab.scroll_up(e)
        self.draw(e)

    def handle_event_click(self, e):
        # Convert the screen coordinates to page coordinates.
        x, y = e.x, e.y
        y += self.active_tab.scrollbar.scroll

        # Perform a hit test. Get the list of layout objects that have been clicked.
        tree = self.tree_to_list(self.active_tab.document, [])
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
                url = self.active_tab.url.resolve(elt.attributes["href"])
                self.active_tab.load(url)
                self.draw()
            elt = elt.parent

    def tree_to_list(self, tree, list):
        list.append(tree)
        for child in tree.children:
            self.tree_to_list(child, list)
        return list

if __name__ == "__main__":
    import sys
    Browser().new_tab(Url(sys.argv[1]))
    tkinter.mainloop()